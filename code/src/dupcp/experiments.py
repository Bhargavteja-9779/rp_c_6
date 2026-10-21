"""Experiment drivers. Every number written to results/ is computed here from model outputs."""
from __future__ import annotations

import json
import os
import time
import traceback

import numpy as np
import pandas as pd

from .audit import audit
from .conformal import (CLS_SCORES, classification_sets, conformal_quantile, test_thresholds,
                        thresholds)
from .data import load_dataset
from .metrics import ece_toplabel, size_matched_ece
from .models import dense_features, fit_predict
from .splits import group_split, random_split

SEEN, NOVEL = 1, 0
DIST_FLOP_CAP = 5e10  # skip the exploratory distance analysis above this brute-force NN cost


def _nanmean(a):
    return float(np.mean(a)) if len(a) else np.nan


def _distance_bins(X, tr, ca, te, seen_ca, seen_te):
    """Exploratory taxonomy: seen -> bin 5; novel -> quintile bin 0..4 of distance to the nearest
    training row, with bin edges taken from leave-one-out NN distances *within the training set*
    (so the taxonomy is a function of training data only)."""
    from sklearn.neighbors import NearestNeighbors
    Z_tr, (Z_ca, Z_te) = dense_features(X.iloc[tr], [X.iloc[ca], X.iloc[te]])
    dim = Z_tr.shape[1]
    if len(tr) * (len(ca) + len(te) + len(tr)) * dim > DIST_FLOP_CAP:
        return None
    nn = NearestNeighbors(n_neighbors=2).fit(Z_tr)
    d_tr = nn.kneighbors(Z_tr, n_neighbors=2, return_distance=True)[0][:, 1]
    pos = d_tr[d_tr > 0]
    if len(pos) < 50:
        return None
    edges = np.quantile(pos, [0.2, 0.4, 0.6, 0.8])
    d_ca = nn.kneighbors(Z_ca, n_neighbors=1)[0][:, 0]
    d_te = nn.kneighbors(Z_te, n_neighbors=1)[0][:, 0]
    b_ca = np.where(seen_ca, 5, np.digitize(d_ca, edges))
    b_te = np.where(seen_te, 5, np.digitize(d_te, edges))
    return b_ca, b_te


def _record(base, cov, size, seen_te, q_vec, n_ca_seen, n_ca_novel, q_seen, q_novel, width_scale=None):
    s, n = seen_te == SEEN, seen_te == NOVEL
    if base.get("method") == "DCP":  # six-bin taxonomy: seen/novel thresholds are not defined
        q_seen = q_novel = np.nan
    r = dict(base)
    r.update(cov_all=_nanmean(cov), cov_seen=_nanmean(cov[s]), cov_novel=_nanmean(cov[n]),
             n_te=len(cov), n_te_seen=int(s.sum()), n_te_novel=int(n.sum()),
             n_ca_seen=int(n_ca_seen), n_ca_novel=int(n_ca_novel),
             q_seen=q_seen, q_novel=q_novel,
             fallback_novel=bool(np.isinf(q_novel)) if n.any() else False,
             fallback_frac=float(np.mean(np.isinf(q_vec))))
    fin = np.isfinite(size)
    r.update(size_all=_nanmean(size), size_seen=_nanmean(size[s]), size_novel=_nanmean(size[n]),
             size_all_finite=_nanmean(size[fin]))
    if width_scale is not None:
        r.update(size_all_norm=r["size_all"] / width_scale, size_seen_norm=r["size_seen"] / width_scale,
                 size_novel_norm=r["size_novel"] / width_scale)
    return r


def _cp_methods(proto, seen_ca, seen_te, bins):
    """(method name, calibration groups, test groups, group labels)."""
    out = [("SCP", None, None, None)]
    if proto == "R":
        out.append(("MCP", seen_ca, seen_te, (NOVEL, SEEN)))
        if bins is not None:
            out.append(("DCP", bins[0], bins[1], tuple(range(6))))
    return out


def run_dataset(data_id: int, task: str, cfg: dict, out_dir: str) -> str:
    path = os.path.join(out_dir, f"{task}_{data_id}.csv")
    if os.path.exists(path):
        return "cached"
    t0 = time.time()
    d = load_dataset(data_id, task, cfg["cache_dir"])
    X, y, keys = d["X"], d["y"], d["keys"]
    aud = audit(keys, y, task, cfg["fracs"][0])
    aud.update(data_id=data_id, task=task, name=d["name"], n_raw=d["n_raw"], subsampled=d["subsampled"],
               n_features=X.shape[1], dropped_missing_target=d["dropped_missing_target"])
    K = int(y.max()) + 1 if task == "classification" else None
    aud["n_classes"] = K
    rows, calib_rows, dist_rows = [], [], []
    rng = np.random.default_rng(data_id)
    for seed in cfg["seeds"]:
        for proto in cfg["protocols"]:
            if proto == "R":
                tr, ca, te = random_split(len(y), seed, cfg["fracs"])
            else:
                tr, ca, te = group_split(keys, seed, cfg["fracs"])
            tr_keys = set(keys[tr].tolist())
            seen_ca = np.array([k in tr_keys for k in keys[ca]], dtype=int)
            seen_te = np.array([k in tr_keys for k in keys[te]], dtype=int)
            bins = None
            if proto == "R" and cfg.get("distance", False):
                try:
                    bins = _distance_bins(X, tr, ca, te, seen_ca == SEEN, seen_te == SEEN)
                except Exception:
                    bins = None
            Xtr, Xca, Xte = X.iloc[tr], X.iloc[ca], X.iloc[te]
            models = list(cfg["models"]) + (["cqr"] if task == "regression" and cfg.get("cqr") else [])
            for model in models:
                base = dict(data_id=data_id, name=d["name"], task=task, seed=seed, protocol=proto, model=model)
                try:
                    if task == "classification":
                        Pc, Pt = fit_predict(model, task, Xtr, y[tr], [Xca, Xte], seed, n_classes=K)
                        conf, pred = Pt.max(1), Pt.argmax(1)
                        correct = (pred == y[te]).astype(float)
                        s, n = seen_te == SEEN, seen_te == NOVEL
                        calib_rows.append(dict(base, acc_all=correct.mean(), acc_seen=_nanmean(correct[s]),
                                               acc_novel=_nanmean(correct[n]),
                                               conf_all=conf.mean(), conf_seen=_nanmean(conf[s]),
                                               conf_novel=_nanmean(conf[n]),
                                               ece_all=ece_toplabel(conf, correct),
                                               ece_seen=ece_toplabel(conf[s], correct[s]),
                                               ece_novel=ece_toplabel(conf[n], correct[n]),
                                               ece_all_sizematched=size_matched_ece(conf, correct, int(n.sum()), rng),
                                               n_te_seen=int(s.sum()), n_te_novel=int(n.sum())))
                        for sname in cfg["cls_scores"]:
                            f = CLS_SCORES[sname]
                            if sname == "aps":  # randomized APS; U fixed per (dataset, seed)
                                urng = np.random.default_rng([data_id, seed, 1 if proto == "R" else 2])
                                Sc, St = f(Pc, urng.random(len(ca))), f(Pt, urng.random(len(te)))
                            else:
                                Sc, St = f(Pc), f(Pt)
                            sc = Sc[np.arange(len(ca)), y[ca]]
                            st = St[np.arange(len(te)), y[te]]
                            for alpha in cfg["alphas"]:
                                for mname, gca, gte, glab in _cp_methods(proto, seen_ca, seen_te, bins):
                                    thr = thresholds(sc, gca, alpha, glab or (0, 1))
                                    q = test_thresholds(thr, gte, len(te))
                                    cov = (st <= q).astype(float)
                                    size = classification_sets(St, q).sum(1).astype(float)
                                    rows.append(_record(dict(base, score=sname, alpha=alpha, method=mname), cov, size, seen_te,
                                                        q, (seen_ca == SEEN).sum(), (seen_ca == NOVEL).sum(),
                                                        thr.get(SEEN, thr.get("all")), thr.get(NOVEL, thr.get("all"))))
                                    if mname == "SCP" and bins is not None and alpha == cfg["primary_alpha"]:
                                        for b in range(6):
                                            m = bins[1] == b
                                            dist_rows.append(dict(base, score=sname, alpha=alpha, method="SCP", bin=b,
                                                                  n=int(m.sum()), cov=_nanmean(cov[m]), size=_nanmean(size[m])))
                                    if mname == "DCP" and alpha == cfg["primary_alpha"]:
                                        for b in range(6):
                                            m = bins[1] == b
                                            dist_rows.append(dict(base, score=sname, alpha=alpha, method="DCP", bin=b,
                                                                  n=int(m.sum()), cov=_nanmean(cov[m]), size=_nanmean(size[m])))
                    else:
                        scale = float(np.std(y[tr])) or 1.0
                        if model == "cqr":
                            a = cfg["primary_alpha"]
                            lo_c, lo_t = fit_predict("lgbm_q_lo", task, Xtr, y[tr], [Xca, Xte], seed, quantile=a / 2)
                            hi_c, hi_t = fit_predict("lgbm_q_hi", task, Xtr, y[tr], [Xca, Xte], seed, quantile=1 - a / 2)
                            sc = np.maximum(lo_c - y[ca], y[ca] - hi_c)
                            st = np.maximum(lo_t - y[te], y[te] - hi_t)
                            base_w = np.maximum(hi_t - lo_t, 0)
                            alphas, sname = [a], "cqr"
                        else:
                            yc, yt = fit_predict(model, task, Xtr, y[tr], [Xca, Xte], seed)
                            sc, st = np.abs(y[ca] - yc), np.abs(y[te] - yt)
                            base_w = np.zeros(len(te))
                            alphas, sname = cfg["alphas"], "absres"
                        for alpha in alphas:
                            for mname, gca, gte, glab in _cp_methods(proto, seen_ca, seen_te, bins):
                                thr = thresholds(sc, gca, alpha, glab or (0, 1))
                                q = test_thresholds(thr, gte, len(te))
                                cov = (st <= q).astype(float)
                                width = base_w + 2 * q
                                rows.append(_record(dict(base, score=sname, alpha=alpha, method=mname), cov, width, seen_te,
                                                    q, (seen_ca == SEEN).sum(), (seen_ca == NOVEL).sum(),
                                                    thr.get(SEEN, thr.get("all")), thr.get(NOVEL, thr.get("all")),
                                                    width_scale=scale))
                                if bins is not None and alpha == cfg["primary_alpha"] and mname in ("SCP", "DCP"):
                                    for b in range(6):
                                        m = bins[1] == b
                                        dist_rows.append(dict(base, score=sname, alpha=alpha, method=mname, bin=b,
                                                              n=int(m.sum()), cov=_nanmean(cov[m]),
                                                              size=_nanmean(width[m]) / scale))
                except Exception as e:  # recorded, never silently dropped
                    rows.append(dict(base, error=repr(e)[:300], trace=traceback.format_exc()[-800:]))
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(path + ".tmp", index=False)
    if calib_rows:
        pd.DataFrame(calib_rows).to_csv(os.path.join(out_dir, f"calib_{task}_{data_id}.csv"), index=False)
    if dist_rows:
        pd.DataFrame(dist_rows).to_csv(os.path.join(out_dir, f"dist_{task}_{data_id}.csv"), index=False)
    aud["seconds"] = round(time.time() - t0, 1)
    json.dump(aud, open(os.path.join(out_dir, f"audit_{task}_{data_id}.json"), "w"), indent=1)
    os.replace(path + ".tmp", path)
    return f"done {time.time() - t0:.0f}s"


# ---------------------------------------------------------------- controlled experiments
def inject_duplicates(X: pd.DataFrame, y: np.ndarray, rate: float, seed: int):
    """Append one exact copy (features and label) of round(rate*N) randomly chosen rows."""
    rng = np.random.default_rng(seed + 777)
    n = len(y)
    k = int(round(rate * n))
    pick = rng.choice(n, size=k, replace=False)
    X2 = pd.concat([X, X.iloc[pick]], ignore_index=True)
    y2 = np.concatenate([y, y[pick]])
    return X2, y2


def run_injection(data_id: int, task: str, cfg: dict, out_dir: str) -> str:
    from .data import row_keys
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"inject_{task}_{data_id}.csv")
    if os.path.exists(path):
        return "cached"
    t0 = time.time()
    d = load_dataset(data_id, task, cfg["cache_dir"])
    X0, y0 = d["X"], d["y"]
    if len(y0) > cfg["inject_max_rows"]:
        idx = np.random.default_rng(data_id).choice(len(y0), cfg["inject_max_rows"], replace=False)
        X0, y0 = X0.iloc[idx].reset_index(drop=True), y0[idx]
    K = int(d["y"].max()) + 1 if task == "classification" else None
    rows = []
    a = cfg["primary_alpha"]
    for rate in cfg["inject_rates"]:
        for seed in cfg["inject_seeds"]:
            X, y = inject_duplicates(X0, y0, rate, seed)
            keys = row_keys(X)
            tr, ca, te = random_split(len(y), seed, cfg["fracs"])
            tr_keys = set(keys[tr].tolist())
            seen_ca = np.array([k in tr_keys for k in keys[ca]], dtype=int)
            seen_te = np.array([k in tr_keys for k in keys[te]], dtype=int)
            pred_pi = audit(keys, y, task, cfg["fracs"][0])["pred_exposure"]
            for model in cfg["inject_models"]:
                base = dict(data_id=data_id, name=d["name"], task=task, rate=rate, seed=seed, model=model,
                            pred_exposure=pred_pi)
                try:
                    if task == "classification":
                        Pc, Pt = fit_predict(model, task, X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed, n_classes=K)
                        sc = 1 - Pc[np.arange(len(ca)), y[ca]]
                        st = 1 - Pt[np.arange(len(te)), y[te]]
                    else:
                        yc, yt = fit_predict(model, task, X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed)
                        sc, st = np.abs(y[ca] - yc), np.abs(y[te] - yt)
                    for mname, gca, gte, glab in _cp_methods("R", seen_ca, seen_te, None):
                        thr = thresholds(sc, gca, a, glab or (0, 1))
                        q = test_thresholds(thr, gte, len(te))
                        cov = (st <= q).astype(float)
                        rows.append(_record(dict(base, method=mname), cov, np.zeros(len(te)), seen_te, q,
                                            (seen_ca == SEEN).sum(), (seen_ca == NOVEL).sum(),
                                            thr.get(SEEN, thr.get("all")), thr.get(NOVEL, thr.get("all"))))
                except Exception as e:
                    rows.append(dict(base, error=repr(e)[:300]))
    pd.DataFrame(rows).to_csv(path, index=False)
    return f"done {time.time() - t0:.0f}s"


CAPACITY_GRID = {
    "knn": [{"k": 1}, {"k": 5}, {"k": 25}, {"k": 100}],
    "rf": [{"min_samples_leaf": 1}, {"min_samples_leaf": 5}, {"min_samples_leaf": 25}, {"min_samples_leaf": 100}],
    "logreg": [{"C": 100.0, "alpha": 0.01}, {"C": 1.0, "alpha": 1.0}, {"C": 0.01, "alpha": 100.0}],
}


def run_capacity(data_id: int, task: str, cfg: dict, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"capacity_{task}_{data_id}.csv")
    if os.path.exists(path):
        return "cached"
    t0 = time.time()
    d = load_dataset(data_id, task, cfg["cache_dir"])
    X, y, keys = d["X"], d["y"], d["keys"]
    K = int(y.max()) + 1 if task == "classification" else None
    a = cfg["primary_alpha"]
    rows = []
    for seed in cfg["capacity_seeds"]:
        tr, ca, te = random_split(len(y), seed, cfg["fracs"])
        tr_keys = set(keys[tr].tolist())
        seen_ca = np.array([k in tr_keys for k in keys[ca]], dtype=int)
        seen_te = np.array([k in tr_keys for k in keys[te]], dtype=int)
        for model, grid in CAPACITY_GRID.items():
            for level, kw in enumerate(grid):
                base = dict(data_id=data_id, name=d["name"], task=task, seed=seed, model=model,
                            level=level, params=json.dumps(kw))
                kw2 = {k: v for k, v in kw.items() if not (model == "logreg" and k == ("alpha" if task == "classification" else "C"))}
                try:
                    if task == "classification":
                        Pc, Pt = fit_predict(model, task, X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed, n_classes=K, **kw2)
                        sc = 1 - Pc[np.arange(len(ca)), y[ca]]
                        st = 1 - Pt[np.arange(len(te)), y[te]]
                    else:
                        yc, yt = fit_predict(model, task, X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed, **kw2)
                        sc, st = np.abs(y[ca] - yc), np.abs(y[te] - yt)
                    for mname, gca, gte, glab in _cp_methods("R", seen_ca, seen_te, None):
                        thr = thresholds(sc, gca, a, glab or (0, 1))
                        q = test_thresholds(thr, gte, len(te))
                        cov = (st <= q).astype(float)
                        rows.append(_record(dict(base, method=mname), cov, np.zeros(len(te)), seen_te, q,
                                            (seen_ca == SEEN).sum(), (seen_ca == NOVEL).sum(),
                                            thr.get(SEEN, thr.get("all")), thr.get(NOVEL, thr.get("all"))))
                except Exception as e:
                    rows.append(dict(base, error=repr(e)[:300]))
    pd.DataFrame(rows).to_csv(path, index=False)
    return f"done {time.time() - t0:.0f}s"


def run_normalized(data_id: int, task: str, cfg: dict, out_dir: str) -> str:
    """Review-round-2 baseline: kNN-difficulty normalized residual score (regression)."""
    from sklearn.neighbors import NearestNeighbors
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"normalized_{task}_{data_id}.csv")
    if os.path.exists(path):
        return "cached"
    t0 = time.time()
    d = load_dataset(data_id, task, cfg["cache_dir"])
    X, y, keys = d["X"], d["y"], d["keys"]
    a = cfg["primary_alpha"]
    rows = []
    for seed in cfg["seeds"]:
        tr, ca, te = random_split(len(y), seed, cfg["fracs"])
        tr_keys = set(keys[tr].tolist())
        seen_ca = np.array([k in tr_keys for k in keys[ca]], dtype=int)
        seen_te = np.array([k in tr_keys for k in keys[te]], dtype=int)
        Z_tr, (Z_ca, Z_te) = dense_features(X.iloc[tr], [X.iloc[ca], X.iloc[te]])
        nn = NearestNeighbors(n_neighbors=10).fit(Z_tr)
        sig_ca = nn.kneighbors(Z_ca)[0].mean(1)
        sig_te = nn.kneighbors(Z_te)[0].mean(1)
        beta = float(np.median(sig_ca)) or 1e-8
        for model in ("rf", "lgbm"):
            base = dict(data_id=data_id, name=d["name"], task=task, seed=seed, model=model, score="normres", alpha=a)
            yc, yt = fit_predict(model, task, X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed)
            sc = np.abs(y[ca] - yc) / (sig_ca + beta)
            st = np.abs(y[te] - yt) / (sig_te + beta)
            scale = float(np.std(y[tr])) or 1.0
            for mname, gca, gte, glab in _cp_methods("R", seen_ca, seen_te, None):
                thr = thresholds(sc, gca, a, glab or (0, 1))
                q = test_thresholds(thr, gte, len(te))
                cov = (st <= q).astype(float)
                width = 2 * q * (sig_te + beta)
                rows.append(_record(dict(base, method=mname), cov, width, seen_te, q, (seen_ca == SEEN).sum(),
                                    (seen_ca == NOVEL).sum(), thr.get(SEEN, thr.get("all")),
                                    thr.get(NOVEL, thr.get("all")), width_scale=scale))
    pd.DataFrame(rows).to_csv(path, index=False)
    return f"done {time.time() - t0:.0f}s"
