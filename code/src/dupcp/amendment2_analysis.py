"""Analyses pre-specified in Amendment 2: validation wave 2 (W1–W5) and the remedy comparison.

Writes results/reinforcement/statistics_amendment2.json and tables/remedies_summary.csv,
tables/screening.csv.
"""
from __future__ import annotations

import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from .analysis import boot_ci_median, holm, wilcoxon_1s

A = 0.1
TOL = 0.02


def _gstar(pi_p):
    return -(1 - A) if pi_p >= 1 - A else -A * pi_p / (1 - pi_p)


def _wave(res, folder, prefix, selection):
    R = os.path.join(res, "reinforcement")
    files = glob.glob(os.path.join(R, folder, f"{prefix}_*.csv"))
    if not files:
        return pd.DataFrame()
    P = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    if "error" in P:
        P = P[P.error.isna()]
    P = P[P.score.isin(["lac", "absres"])]
    sel = json.load(open(os.path.join(R, selection)))
    pe = {str(x["data_id"]): x["pred_exposure"] for x in sel["included"]}
    g = P.groupby(["data_id", "name", "task", "model", "method"]).agg(
        cov_novel=("cov_novel", "mean"), pi=("pi", "mean"), pi_p=("pi_p", "mean"),
        bad=("cov_novel", lambda v: float(np.mean(v < 0.87)))).reset_index()
    g["gap"] = g.cov_novel - (1 - A)
    g["g_star"] = g.pi_p.map(_gstar)
    g["pred_exposure"] = g.data_id.astype(str).map(pe)
    return g


def _exact_ci(k, n):
    if n == 0:
        return (np.nan, np.nan)
    lo = stats.beta.ppf(0.025, k, n - k + 1) if k > 0 else 0.0
    hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return (float(lo), float(hi))


def screening(g):
    """W1: combined flag (g* < -2 pp or pred. exposure >= 10%) vs positives (SCP gap < -2 pp for RF or LGBM)."""
    s = g[g.method == "SCP"]
    rows = []
    for (did, name), q in s.groupby(["data_id", "name"]):
        qq = q.set_index("model")
        gs, pe = qq.g_star.iloc[0], qq.pred_exposure.iloc[0]
        rows.append(dict(data_id=did, name=name, task=q.task.iloc[0], pred_exposure=pe, g_star=gs,
                         flag=bool(gs < -TOL or pe >= 0.10), flag_gstar=bool(gs < -TOL),
                         positive=bool(any(qq.loc[m, "gap"] < -TOL for m in ("rf", "lgbm") if m in qq.index)),
                         gap_rf=qq.gap.get("rf", np.nan), gap_lgbm=qq.gap.get("lgbm", np.nan),
                         gap_logreg=qq.gap.get("logreg", np.nan), worst_gap=q.gap.min()))
    return pd.DataFrame(rows)


def _w1(sc):
    pos = sc[sc.positive]
    k, n = int(pos.flag.sum()), len(pos)
    neg = sc[~sc.positive]
    unfl = sc[~sc.flag]
    p = float(stats.binomtest(k, n, 0.5, alternative="greater").pvalue) if n else np.nan
    return dict(n_datasets=len(sc), n_positive=n, n_flag=int(sc.flag.sum()), sensitivity=k / n if n else np.nan,
                sensitivity_ci=_exact_ci(k, n), p_sens_gt_half=p,
                specificity=float((~neg.flag).mean()) if len(neg) else np.nan, n_negative=len(neg),
                n_unflagged=len(unfl), worst_gap_unflagged=float(unfl.worst_gap.min()) if len(unfl) else np.nan,
                misses=pos[~pos.flag].name.tolist(),
                sensitivity_gstar_only=float(pos.flag_gstar.mean()) if n else np.nan)


def run(res):
    R = os.path.join(res, "reinforcement")
    T = os.path.join(R, "tables")
    out = {}
    w1 = _wave(res, "prospective", "prosp", "prospective_selection.json")
    w2 = _wave(res, "prospective_w2", "w2", "prospective_selection_w2.json") \
        if os.path.exists(os.path.join(R, "prospective_selection_w2.json")) else pd.DataFrame()
    tb1 = _wave(res, "tiebreak_w1", "tb", "prospective_selection.json")
    # ---------------- W1 (screening): wave 2, and pooled with wave 1
    sc1 = screening(w1)
    sc1["wave"] = 1
    scs = [sc1]
    if len(w2):
        sc2 = screening(w2)
        sc2["wave"] = 2
        scs.append(sc2)
        out["W1_wave2"] = _w1(sc2)
        n2 = w2.data_id.nunique()
        out["wave2_n"] = int(n2)
        out["wave2_tasks"] = w2.drop_duplicates("data_id").task.value_counts().to_dict()
        # ---------------- W2 (fix), W3 (bound), W4 (rank)
        out["W2"], out["W3_W4"] = [], []
        for m in ("rf", "lgbm", "logreg"):
            q = w2[(w2.model == m) & (w2.method == "MCP")]
            lo, hi = boot_ci_median(q.gap.values)
            p = wilcoxon_1s(q.gap.values + 0.01, "greater")[0]
            out["W2"].append(dict(learner=m, n=len(q), median_gap=float(q.gap.median()), ci=(lo, hi),
                                  noninferior=bool(lo > -0.01), worst=float(q.gap.min()), p_wilcoxon=p,
                                  bad_mean=float(q.bad.mean())))
            for meth in ("PAC_MCP", "DCP", "SCP"):
                qq = w2[(w2.model == m) & (w2.method == meth)]
                out.setdefault("W2_other", []).append(dict(learner=m, method=meth, n=len(qq),
                                                           median_gap=float(qq.gap.median()),
                                                           worst=float(qq.gap.min()), bad_mean=float(qq.bad.mean())))
            s = w2[(w2.model == m) & (w2.method == "SCP")]
            k = int((s.gap >= s.g_star - TOL).sum())
            rho, p2 = stats.spearmanr(s.g_star, s.gap)
            out["W3_W4"].append(dict(learner=m, n=len(s), share_above=k / len(s), share_ci=_exact_ci(k, len(s)),
                                     rho=float(rho), p_one_sided=float(p2 / 2 if rho > 0 else 1 - p2 / 2)))
        prim = [out["W1_wave2"]["p_sens_gt_half"], next(x for x in out["W2"] if x["learner"] == "rf")["p_wilcoxon"]]
        out["holm_W1_W2rf"] = list(map(float, holm([p if p == p else 1.0 for p in prim])))
    sc = pd.concat(scs, ignore_index=True)
    out["W1_pooled"] = _w1(sc)
    out["W1_wave1"] = _w1(sc1)
    sc.to_csv(os.path.join(T, "screening.csv"), index=False)
    # ---------------- W5: tie-breaking (pooled, pred. exposure >= 0.10, RF)
    rand = []
    if len(tb1):
        rand.append(tb1[(tb1.method == "SCP_rand")])
    if len(w2):
        rand.append(w2[w2.method == "SCP_rand"])
    if rand:
        rd = pd.concat(rand)
        base = pd.concat([w1[w1.method == "SCP"]] + ([w2[w2.method == "SCP"]] if len(w2) else []))
        mrg = base.merge(rd[["data_id", "model", "gap"]], on=["data_id", "model"], suffixes=("", "_rand"))
        q = mrg[(mrg.model == "rf") & (mrg.pred_exposure >= 0.10)]
        over, over_r = q.gap.clip(lower=0), q.gap_rand.clip(lower=0)
        p = wilcoxon_1s((over - over_r).values, "greater")[0]
        allrf = mrg[mrg.model == "rf"]
        rho_r, prr = stats.spearmanr(allrf.g_star, allrf.gap_rand)
        rho_s, prs = stats.spearmanr(allrf.g_star, allrf.gap)
        out["W5"] = dict(n=len(q), median_over_scp=float(over.median()), median_over_rand=float(over_r.median()),
                         mean_over_scp=float(over.mean()), mean_over_rand=float(over_r.mean()), p_wilcoxon=p,
                         rho_gstar_rand=float(rho_r), p_rand=float(prr / 2 if rho_r > 0 else 1 - prr / 2),
                         rho_gstar_scp=float(rho_s), n_rho=len(allrf),
                         per_dataset=q[["name", "gap", "gap_rand", "g_star", "pred_exposure"]].round(4).to_dict("records"))
        mrg.to_csv(os.path.join(T, "tiebreak.csv"), index=False)
    # ---------------- remedy comparison
    rf = glob.glob(os.path.join(R, "remedies", "remedies_*.csv"))
    if rf:
        Rm = pd.concat([pd.read_csv(f) for f in rf], ignore_index=True)
        out["remedy_errors"] = Rm[Rm.get("error", pd.Series(dtype=str)).notna()][["name", "model", "method"]] \
            .drop_duplicates().to_dict("records") if "error" in Rm else []
        Rm = Rm[(Rm.method != "error") & (Rm.get("error", pd.Series(np.nan, index=Rm.index)).isna())]
        g = Rm.groupby(["name", "model", "method"])[["cov_new", "cov_seen", "size_new", "size_seen", "empty_new",
                                                     "acc_new", "n_train", "n_cal"]].mean().reset_index()
        g.to_csv(os.path.join(T, "remedies_summary.csv"), index=False)
        med = g.groupby(["model", "method"])[["cov_new", "cov_seen", "size_new", "size_seen", "empty_new"]].median()
        out["remedies_median"] = med.reset_index().to_dict("records")
        worst = g.groupby(["model", "method"]).cov_new.min()
        out["remedies_worst_new"] = worst.reset_index().to_dict("records")
    json.dump(out, open(os.path.join(R, "statistics_amendment2.json"), "w"), indent=1, default=float)
    return out


if __name__ == "__main__":
    import sys
    print(json.dumps(run(sys.argv[1] if len(sys.argv) > 1 else "results"), indent=1, default=float)[:3000])


def fig_screen(res):
    """All fresh data sets (waves 1 and 2): predicted worst-case gap vs observed random-forest gap."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .analysis import C, GRID, INK, INK2
    from .figures import MM, _save
    R = os.path.join(res, "reinforcement")
    sc = pd.read_csv(os.path.join(R, "tables", "screening.csv"))
    sc["obs"] = sc[["gap_rf", "gap_lgbm"]].min(axis=1)
    fig, ax = plt.subplots(figsize=(84 * MM, 78 * MM))
    lo = 100 * min(sc.g_star.min(), sc.obs.min()) - 4
    ax.axhspan(lo, -2, color="#fbe3dc", lw=0, zorder=0)
    ax.plot([lo, 2], [lo, 2], color=INK2, ls="--", lw=0.8, zorder=1, label="Observed = predicted")
    ax.axhline(0, color=INK, lw=0.8, zorder=1)
    for wave, mk, col in ((1, "o", C[0]), (2, "D", C[1])):
        q = sc[sc.wave == wave]
        for flag in (True, False):
            qq = q[q.flag == flag]
            ax.scatter(100 * qq.g_star, 100 * qq.obs, s=18, marker=mk, linewidth=0.9, zorder=3,
                       facecolor=col if flag else "white", edgecolor=col,
                       label=f"Wave {wave}, {'flagged' if flag else 'not flagged'}")
    for _, r in sc[sc.obs < -0.05].iterrows():
        nm = r["name"].replace("analcatdata_", "").replace(" (Android Permissions)", "").replace(
            "Early Stage Diabetes Risk Prediction", "early diabetes").replace("Congressional Voting Records", "voting")
        ax.annotate(nm, (100 * r.g_star, 100 * r.obs), xytext=(4, -2), textcoords="offset points", fontsize=5.8,
                    color=INK2)
    ax.set_xlim(lo, 3)
    ax.set_ylim(lo, 12)
    ax.set_xlabel("Predicted worst-case gap from the check (pp)")
    ax.set_ylabel("Observed gap on new cases (pp)\n(worse of random forest and LightGBM)")
    ax.grid(True, color=GRID)
    ax.legend(loc="lower right", fontsize=5.8, frameon=False)
    _save(fig, os.path.join(R, "figures"), "Fig_screen")
