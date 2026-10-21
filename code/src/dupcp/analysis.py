"""Statistical analysis, tables and figures, generated only from files in results/.

Implements the statistical analysis plan of research_design/experimental_protocol.md (section 8).
Unit of analysis: dataset (metrics averaged over seeds first).
"""
from __future__ import annotations

import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

ALPHA0 = 0.1
LEARNERS = ["logreg", "rf", "lgbm", "knn", "mlp"]
LEARNER_LABEL = {"logreg": "LR / ridge", "rf": "Random forest", "lgbm": "LightGBM", "knn": "k-NN",
                 "mlp": "MLP", "cqr": "CQR (LightGBM)"}
# categorical palette (reference instance of the dataviz skill), fixed order
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
RNG = np.random.default_rng(20261020)


# ------------------------------------------------------------------ helpers
def holm(p):
    p = np.asarray(p, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    m = len(p)
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * p[i]))
        adj[i] = run
    return adj


def boot_ci_median(x, n=10000):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return (np.nan, np.nan)
    b = np.median(RNG.choice(x, size=(n, len(x)), replace=True), axis=1)
    return tuple(np.percentile(b, [2.5, 97.5]))


def wilcoxon_1s(x, alternative):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    x = x[x != 0]
    if len(x) < 5:
        return np.nan, len(x)
    return float(stats.wilcoxon(x, alternative=alternative).pvalue), len(x)


def rank_biserial(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x) & (x != 0)]
    if len(x) == 0:
        return np.nan
    r = stats.rankdata(np.abs(x))
    return float((r[x > 0].sum() - r[x < 0].sum()) / r.sum())


def load(res):
    raw = os.path.join(res, "raw")
    main = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(raw, "classification_*.csv"))
                      + glob.glob(os.path.join(raw, "regression_*.csv"))], ignore_index=True)
    calib = [pd.read_csv(f) for f in glob.glob(os.path.join(raw, "calib_*.csv"))]
    calib = pd.concat(calib, ignore_index=True) if calib else pd.DataFrame()
    dist = [pd.read_csv(f) for f in glob.glob(os.path.join(raw, "dist_*.csv"))]
    dist = pd.concat(dist, ignore_index=True) if dist else pd.DataFrame()
    aud = pd.DataFrame([json.load(open(f)) for f in glob.glob(os.path.join(raw, "audit_*.json"))])
    return main, calib, dist, aud


def analysis_sets(aud):
    aud = aud.copy()
    aud["set"] = np.where(aud["excess_row_frac"] == 0, "CLEAN",
                          np.where(aud["pred_exposure"] >= 0.01, "DUP", "LOW"))
    return aud


# ------------------------------------------------------------------ main
def run(res, cfg, quick=False):
    out_stats = {}
    tables = os.path.join(res, "tables")
    figs = os.path.join(res, "figures")
    os.makedirs(tables, exist_ok=True)
    os.makedirs(figs, exist_ok=True)
    main, calib, dist, aud = load(res)
    aud = analysis_sets(aud)
    errors = main[main["error"].notna()] if "error" in main else pd.DataFrame()
    out_stats["errors"] = {"n_error_rows": int(len(errors)),
                           "by_model": errors.groupby("model").size().to_dict() if len(errors) else {}}
    if len(errors):
        errors[["data_id", "name", "task", "seed", "protocol", "model", "error"]].to_csv(
            os.path.join(tables, "errors.csv"), index=False)
    main = main[main["error"].isna()] if "error" in main else main
    main["exposure"] = main["n_te_seen"] / main["n_te"]

    # ---------------- RQ1: audit + predicted vs observed exposure
    obs = (main[(main.protocol == "R") & (main.method == "SCP")]
           .groupby(["task", "data_id"])["exposure"].mean().rename("obs_exposure"))
    aud = aud.merge(obs, left_on=["task", "data_id"], right_index=True, how="left")
    aud.sort_values(["task", "dup_row_frac"], ascending=[True, False]).to_csv(
        os.path.join(tables, "T1_audit.csv"), index=False)
    a_ok = aud.dropna(subset=["obs_exposure"])
    out_stats["rq1"] = {
        "n_datasets": int(len(aud)),
        "n_by_task": aud.groupby("task").size().to_dict(),
        "sets": aud.groupby(["task", "set"]).size().unstack(fill_value=0).to_dict(),
        "n_with_any_duplicate": int((aud.excess_row_frac > 0).sum()),
        "n_dup_row_frac_ge_0.01": int((aud.dup_row_frac >= 0.01).sum()),
        "n_dup_row_frac_ge_0.30": int((aud.dup_row_frac >= 0.30).sum()),
        "n_conflicting": int((aud.conflict_row_frac > 0).sum()),
        "pred_vs_obs_exposure_mae": float(np.mean(np.abs(a_ok.pred_exposure - a_ok.obs_exposure))),
        "pred_vs_obs_exposure_max_abs_err": float(np.max(np.abs(a_ok.pred_exposure - a_ok.obs_exposure))),
        "pred_vs_obs_pearson": float(np.corrcoef(a_ok.pred_exposure, a_ok.obs_exposure)[0, 1]),
        "subsampled": aud.loc[aud.subsampled, ["task", "data_id", "name", "n_raw"]].to_dict("records"),
    }
    sets = aud.set_index(["task", "data_id"])["set"]

    # ---------------- per-dataset aggregation (seed means)
    keys = ["task", "data_id", "name", "protocol", "model", "score", "alpha", "method"]
    num = ["cov_all", "cov_seen", "cov_novel", "size_all", "size_seen", "size_novel", "exposure",
           "fallback_novel", "fallback_frac", "n_ca_novel", "n_te_novel"]
    num += [c for c in ["size_all_norm", "size_seen_norm", "size_novel_norm"] if c in main]
    agg = main.groupby(keys, dropna=False)[num].mean().reset_index()
    agg["set"] = [sets.get((t, i), "NA") for t, i in zip(agg.task, agg.data_id)]
    agg.to_csv(os.path.join(tables, "per_dataset_results.csv"), index=False)

    fam_list = [("classification", m, s) for m in LEARNERS for s in ("lac", "aps")] + \
               [("regression", m, "absres") for m in LEARNERS] + [("regression", "cqr", "cqr")]

    def fam(task, model, score, method, protocol="R", alpha=ALPHA0, dset="DUP"):
        q = agg[(agg.task == task) & (agg.model == model) & (agg.score == score) & (agg.method == method)
                & (agg.protocol == protocol) & np.isclose(agg.alpha, alpha)]
        if dset:
            q = q[q.set == dset]
        return q.set_index("data_id")

    # ---------------- H1 (primary) + H2 + H3, at each alpha
    for alpha in sorted(agg.alpha.unique()):
        rows = []
        for task, model, score in fam_list:
            s = fam(task, model, score, "SCP", alpha=alpha)
            m = fam(task, model, score, "MCP", alpha=alpha)
            if len(s) == 0:
                continue
            gap = s.cov_novel - (1 - alpha)
            p1, n1 = wilcoxon_1s(gap, "less")
            lo, hi = boot_ci_median(gap)
            j = s.index.intersection(m.index)
            d = (m.cov_novel - s.cov_novel).loc[j]
            p2, n2 = wilcoxon_1s(d, "greater")
            mgap = m.cov_novel - (1 - alpha)
            mlo, mhi = boot_ci_median(mgap)
            exp_ = s.exposure
            rho, prho = (stats.spearmanr(exp_, gap, nan_policy="omit") if gap.notna().sum() > 4 else (np.nan, np.nan))
            limit = (1 - alpha / (1 - exp_.clip(upper=0.99)))
            frac_limit = ((1 - alpha) - s.cov_novel) / ((1 - alpha) - limit)
            szcol = "size_novel_norm" if task == "regression" else "size_novel"
            sacol = "size_all_norm" if task == "regression" else "size_all"
            sscol = "size_seen_norm" if task == "regression" else "size_seen"
            fin = lambda a: a.replace([np.inf, -np.inf], np.nan)
            r_nov = fin(m[szcol].loc[j] / s[szcol].loc[j])
            r_all = fin(m[sacol].loc[j] / s[sacol].loc[j])
            r_seen = fin(m[sscol].loc[j] / s[sscol].loc[j])
            rows.append(dict(task=task, model=model, score=score, alpha=alpha, n_datasets=int(gap.notna().sum()),
                             scp_novel_cov_median=float(s.cov_novel.median()), scp_gap_median=float(gap.median()),
                             scp_gap_ci_lo=lo, scp_gap_ci_hi=hi, scp_gap_mean=float(gap.mean()),
                             scp_gap_min=float(gap.min()),
                             share_gap_lt_minus001=float((gap < -0.01).mean()),
                             p_H1=p1, rank_biserial_H1=rank_biserial(gap),
                             scp_seen_cov_median=float(s.cov_seen.median()),
                             scp_all_cov_median=float(s.cov_all.median()),
                             spearman_exposure_gap=float(rho), p_spearman=float(prho),
                             frac_of_memorization_limit_median=float(frac_limit.replace([np.inf, -np.inf], np.nan).median()),
                             mcp_novel_cov_median=float(m.cov_novel.median()), mcp_gap_median=float(mgap.median()),
                             mcp_gap_ci_lo=mlo, mcp_gap_ci_hi=mhi, mcp_seen_cov_median=float(m.cov_seen.median()),
                             mcp_all_cov_median=float(m.cov_all.median()),
                             p_H2=p2, mcp_minus_scp_novel_median=float(d.median()),
                             mcp_novel_fallback_datasets=int((m.fallback_novel > 0).sum()),
                             size_ratio_novel_median=float(r_nov.median()), size_ratio_seen_median=float(r_seen.median()),
                             size_ratio_all_median=float(r_all.median()),
                             p_H3_all_two_sided=wilcoxon_1s(np.log(r_all.dropna()), "two-sided")[0] if r_all.notna().sum() > 4 else np.nan))
        T = pd.DataFrame(rows)
        if len(T):
            T["p_H1_holm"] = holm(T.p_H1.fillna(1))
            T["p_H2_holm"] = holm(T.p_H2.fillna(1))
        T.to_csv(os.path.join(tables, f"T2_main_alpha{alpha:g}.csv"), index=False)
        out_stats[f"main_alpha_{alpha:g}"] = T.to_dict("records")

    # ---------------- H1b: Friedman across learners
    fr = {}
    for task, score in [("classification", "lac"), ("classification", "aps"), ("regression", "absres")]:
        W = pd.concat({m: fam(task, m, score, "SCP").cov_novel for m in LEARNERS}, axis=1).dropna()
        if len(W) >= 5:
            st = stats.friedmanchisquare(*[W[m] for m in LEARNERS])
            pairs, ps = [], []
            for i, a in enumerate(LEARNERS):
                for b in LEARNERS[i + 1:]:
                    p = stats.wilcoxon(W[a], W[b]).pvalue
                    pairs.append((a, b, float((W[a] - W[b]).median())))
                    ps.append(p)
            ph = holm(ps)
            fr[f"{task}_{score}"] = {"n": int(len(W)), "chi2": float(st.statistic), "p": float(st.pvalue),
                                     "median_novel_cov": W.median().to_dict(),
                                     "mean_rank_of_novel_cov(1=lowest)": W.rank(axis=1).mean().to_dict(),
                                     "pairwise": [dict(a=a, b=b, median_diff=md, p_holm=float(p))
                                                  for (a, b, md), p in zip(pairs, ph)]}
    out_stats["H1b_friedman"] = fr

    # ---------------- H6: group-aware split
    h6 = []
    for task, model, score in fam_list:
        g = fam(task, model, score, "SCP", protocol="G")
        if len(g) == 0:
            continue
        gap = g.cov_all - (1 - ALPHA0)
        lo, hi = boot_ci_median(gap)
        h6.append(dict(task=task, model=model, score=score, n=int(gap.notna().sum()),
                       g_cov_median=float(g.cov_all.median()), gap_median=float(gap.median()),
                       ci_lo=lo, ci_hi=hi, noninferior_0_01=bool(lo > -0.01),
                       share_gap_lt_minus001=float((gap < -0.01).mean())))
    pd.DataFrame(h6).to_csv(os.path.join(tables, "T3_group_split.csv"), index=False)
    out_stats["H6_group_split"] = h6

    # ---------------- null control
    nc = []
    for task, model, score in fam_list:
        s = fam(task, model, score, "SCP", dset="CLEAN")
        m = fam(task, model, score, "MCP", dset="CLEAN")
        if len(s):
            nc.append(dict(task=task, model=model, score=score, n=int(len(s)),
                           scp_cov_median=float(s.cov_all.median()), scp_cov_mean=float(s.cov_all.mean()),
                           max_abs_mcp_minus_scp=float((m.cov_all - s.cov_all).abs().max())))
    pd.DataFrame(nc).to_csv(os.path.join(tables, "T4_null_control.csv"), index=False)
    out_stats["null_control"] = nc

    # ---------------- H4: calibration
    if len(calib):
        cal = calib[calib.protocol == "R"].copy()
        cal["oc_all"] = cal.conf_all - cal.acc_all
        cal["oc_novel"] = cal.conf_novel - cal.acc_novel
        cal["oc_seen"] = cal.conf_seen - cal.acc_seen
        ca = cal.groupby(["data_id", "model"])[["oc_all", "oc_novel", "oc_seen", "ece_all", "ece_novel",
                                                "ece_seen", "ece_all_sizematched", "acc_all", "acc_novel",
                                                "acc_seen"]].mean().reset_index()
        ca["set"] = [sets.get(("classification", i), "NA") for i in ca.data_id]
        ca.to_csv(os.path.join(tables, "per_dataset_calibration.csv"), index=False)
        rows = []
        for m in LEARNERS:
            q = ca[(ca.model == m) & (ca.set == "DUP")]
            d1 = q.oc_novel - q.oc_all
            d2 = q.ece_novel - q.ece_all_sizematched
            p1, n1 = wilcoxon_1s(d1, "greater")
            p2, n2 = wilcoxon_1s(d2, "greater")
            rows.append(dict(model=m, n=int(d1.notna().sum()), oc_all_median=float(q.oc_all.median()),
                             oc_novel_median=float(q.oc_novel.median()), oc_seen_median=float(q.oc_seen.median()),
                             oc_diff_median=float(d1.median()), p_oc=p1,
                             ece_all_median=float(q.ece_all.median()), ece_novel_median=float(q.ece_novel.median()),
                             ece_sizematched_median=float(q.ece_all_sizematched.median()),
                             ece_diff_median=float(d2.median()), p_ece=p2,
                             acc_seen_median=float(q.acc_seen.median()), acc_novel_median=float(q.acc_novel.median())))
        T = pd.DataFrame(rows)
        T["p_oc_holm"] = holm(T.p_oc.fillna(1))
        T["p_ece_holm"] = holm(T.p_ece.fillna(1))
        T.to_csv(os.path.join(tables, "T5_calibration.csv"), index=False)
        out_stats["H4_calibration"] = T.to_dict("records")

    # ---------------- exploratory distance bins
    if len(dist):
        dd = dist[np.isclose(dist.alpha, ALPHA0) & dist.score.isin(["lac", "absres"])]
        dd = dd.groupby(["task", "data_id", "model", "method", "bin"])["cov"].mean().reset_index()
        summ = dd.groupby(["task", "method", "bin"])["cov"].agg(["median", "mean", "count"]).reset_index()
        summ.to_csv(os.path.join(tables, "T6_distance_bins.csv"), index=False)
        out_stats["E_distance_bins"] = summ.to_dict("records")
        dist_agg = dd
    else:
        dist_agg = pd.DataFrame()

    # ---------------- Experiments D and F
    inj = _load_glob(os.path.join(res, "inject", "inject_*.csv"))
    cap = _load_glob(os.path.join(res, "capacity", "capacity_*.csv"))
    if len(inj):
        out_stats["D_injection"] = _dose(inj, "rate", tables, "T7_injection")
    if len(cap):
        out_stats["F_capacity"] = _dose(cap, "level", tables, "T8_capacity")

    json.dump(out_stats, open(os.path.join(res, "statistics.json"), "w"), indent=1, default=_js)
    try:
        from . import figures
        figures.make_all(res, agg, aud, calib, dist_agg, inj, cap)
    except Exception as e:  # figures must never silently replace numbers
        print("FIGURE ERROR", repr(e))
        raise
    return out_stats


def _js(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


def _load_glob(pat):
    fs = glob.glob(pat)
    if not fs:
        return pd.DataFrame()
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    if "error" in d:
        d = d[d["error"].isna()]
    d["exposure"] = d["n_te_seen"] / d["n_te"]
    return d


def _dose(df, xvar, tables, name):
    """Within dataset x learner Spearman(x, gap) for SCP; Wilcoxon of correlations vs 0."""
    s = df[df.method == "SCP"].groupby(["task", "data_id", "model", xvar])[["cov_novel", "cov_seen", "exposure"]].mean().reset_index()
    m = df[df.method == "MCP"].groupby(["task", "data_id", "model", xvar])["cov_novel"].mean().rename("mcp_cov_novel").reset_index()
    s = s.merge(m, on=["task", "data_id", "model", xvar], how="left")
    s["gap"] = s.cov_novel - (1 - ALPHA0)
    s["mcp_gap"] = s.mcp_cov_novel - (1 - ALPHA0)
    s["limit_gap"] = -ALPHA0 * s.exposure / (1 - s.exposure.clip(upper=0.99))
    # Proposition 1 prediction using measured seen coverage and exposure (marginal at nominal)
    s["prop1_pred_novel"] = ((1 - ALPHA0) - s.exposure * s.cov_seen) / (1 - s.exposure)
    s.to_csv(os.path.join(tables, f"{name}_per_dataset.csv"), index=False)
    res = {}
    for (task, model), g in s.groupby(["task", "model"]):
        rhos = []
        for _, gg in g.groupby("data_id"):
            gg = gg.dropna(subset=["gap"])
            if gg[xvar].nunique() >= 3 and gg.gap.nunique() > 1:
                rhos.append(stats.spearmanr(gg[xvar], gg.gap)[0])
        rhos = np.array(rhos)
        p = wilcoxon_1s(rhos, "less")[0] if len(rhos) >= 5 else np.nan
        summ = g.groupby(xvar)[["gap", "mcp_gap", "limit_gap", "exposure"]].median().reset_index()
        res[f"{task}_{model}"] = {"n_datasets": int(g.data_id.nunique()), "median_spearman": float(np.median(rhos)) if len(rhos) else np.nan,
                                  "p_spearman_lt0": p, "by_level": summ.to_dict("records")}
    pd.DataFrame([dict(key=k, **{kk: vv for kk, vv in v.items() if kk != "by_level"}) for k, v in res.items()]).to_csv(
        os.path.join(tables, f"{name}_summary.csv"), index=False)
    return res
