"""Analysis of the reinforcement-cycle experiments (revised protocol): purity bound (P1, P2, P5),
remedies (P3), training-conditional reliability (P4), near-duplicates (N1-N3).
Writes results/reinforcement/{statistics_reinforcement.json, tables/*.csv, figures/*}."""
from __future__ import annotations

import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from .analysis import C, INK, INK2, boot_ci_median, holm, wilcoxon_1s
from .audit import purity_bound

A = 0.1
RNG = np.random.default_rng(20261021)


def _spearman_boot_diff(x1, x2, y, n=10000):
    x1, x2, y = map(np.asarray, (x1, x2, y))
    idx = np.arange(len(y))
    d = []
    for _ in range(n):
        b = RNG.choice(idx, len(idx))
        d.append(stats.spearmanr(x1[b], y[b])[0] - stats.spearmanr(x2[b], y[b])[0])
    return float(np.nanpercentile(d, 2.5)), float(np.nanpercentile(d, 97.5))


def purity_tests(df, learner, label):
    """df: one row per dataset with columns g_star, g_pi, gap_scp."""
    q = df.dropna(subset=["gap_scp"])
    out = {"set": label, "learner": learner, "n": int(len(q))}
    if len(q) < 5:
        return out
    r1 = stats.spearmanr(q.g_star, q.gap_scp)
    r2 = stats.spearmanr(q.g_pi, q.gap_scp)
    above = (q.gap_scp >= q.g_star - 0.02)
    k, n = int(above.sum()), len(q)
    ci = stats.binomtest(k, n).proportion_ci(confidence_level=0.95)
    lo, hi = _spearman_boot_diff(q.g_star, q.g_pi, q.gap_scp)
    out.update(rho_gstar=float(r1[0]), p_gstar_one_sided=float(r1[1] / 2 if r1[0] > 0 else 1 - r1[1] / 2),
               rho_gpi=float(r2[0]), rho_diff_ci=[lo, hi], share_above_bound=k / n,
               share_above_ci=[float(ci.low), float(ci.high)],
               median_ratio_obs_to_gstar=float(np.median((q.gap_scp / q.g_star)[q.g_star < -0.01])) if (q.g_star < -0.01).any() else np.nan,
               violations=q.loc[~above, ["name", "pi", "pi_p", "g_star", "gap_scp"]].round(4).to_dict("records") if "name" in q else [])
    return out


def run(res):
    R = os.path.join(res, "reinforcement")
    T = os.path.join(R, "tables")
    F = os.path.join(R, "figures")
    os.makedirs(T, exist_ok=True)
    os.makedirs(F, exist_ok=True)
    S = {}
    # ---------------- retrospective purity (non-blind)
    retro_p = os.path.join(R, "purity_retrospective.csv")
    if os.path.exists(retro_p):
        r = pd.read_csv(retro_p)
        r = r[r.pi >= 0.01]
        S["retrospective"] = [purity_tests(r[r.model == m], m, "retrospective (v1 suites+external)") for m in
                              ["rf", "lgbm", "mlp", "logreg", "knn"]]
        inj = pd.read_csv(os.path.join(R, "purity_injection.csv"))
        inj["g_pi"] = [purity_bound(p, A) for p in inj.pi]
        S["retrospective_injection"] = []
        for m in ["rf", "lgbm", "logreg", "knn"]:
            q = inj[(inj.model == m) & (inj.rate > 0)]
            S["retrospective_injection"].append({"learner": m, "n": int(len(q)),
                                                 "rho_gstar": float(stats.spearmanr(q.g_star, q.gap_scp)[0]),
                                                 "median_ratio_at_rate1": float(np.median((q.gap_scp / q.g_star)[q.rate == 1.0]))})
    # ---------------- prospective
    pf = glob.glob(os.path.join(R, "prospective", "prosp_*.csv"))
    if pf:
        P = pd.concat([pd.read_csv(f) for f in pf], ignore_index=True)
        errs = P[P["error"].notna()] if "error" in P else P.iloc[:0]
        P = P[P["error"].isna()] if "error" in P else P
        S["prospective_errors"] = errs[["data_id", "model", "seed", "error"]].to_dict("records") if len(errs) else []
        base = P[P.score.isin(["lac", "absres"])]
        agg = base.groupby(["task", "data_id", "name", "model", "method"]).agg(
            cov_novel=("cov_novel", "mean"), pi=("pi", "mean"), pi_p=("pi_p", "mean"),
            size_novel=("size_novel", "mean"), bad=("cov_novel", lambda v: float(np.mean(v < 0.87))),
            fallback=("fallback_novel", "mean")).reset_index()
        agg.to_csv(os.path.join(T, "prospective_per_dataset.csv"), index=False)
        scp = agg[agg.method == "SCP"].copy()
        scp["gap_scp"] = scp.cov_novel - (1 - A)
        scp["g_star"] = [purity_bound(p, A) for p in scp.pi_p]
        scp["g_pi"] = [purity_bound(p, A) for p in scp.pi]
        S["prospective_n_datasets"] = int(agg.data_id.nunique())
        S["prospective_tasks"] = agg.groupby("task").data_id.nunique().to_dict()
        S["P1_P2_P5"] = [purity_tests(scp[scp.model == m], m, "prospective") for m in ["rf", "lgbm", "logreg"]]
        # P3 remedies
        p3 = []
        for m in ["rf", "lgbm", "logreg"]:
            for meth in ["SCP", "MCP", "PAC_MCP", "DCP"]:
                q = agg[(agg.model == m) & (agg.method == meth)]
                g = q.cov_novel - (1 - A)
                lo, hi = boot_ci_median(g)
                p3.append(dict(learner=m, method=meth, n=int(g.notna().sum()), median_gap=float(g.median()),
                               ci_lo=lo, ci_hi=hi, worst=float(g.min()), noninferior=bool(lo > -0.01),
                               median_bad_split_rate=float(q.bad.median()), mean_bad_split_rate=float(q.bad.mean()),
                               fallback_rate=float(q.fallback.mean())))
        S["P3"] = p3
        # P4: PAC vs MCP bad-split rate
        p4 = []
        for m in ["rf", "lgbm", "logreg"]:
            a_ = agg[(agg.model == m) & (agg.method == "MCP")].set_index("data_id").bad
            b_ = agg[(agg.model == m) & (agg.method == "PAC_MCP")].set_index("data_id").bad
            j = a_.index.intersection(b_.index)
            diff = (b_.loc[j] - a_.loc[j])
            p4.append(dict(learner=m, n=int(len(j)), mcp_bad_mean=float(a_.loc[j].mean()),
                           pac_bad_mean=float(b_.loc[j].mean()), p_pac_lower=wilcoxon_1s(diff, "less")[0]))
        S["P4"] = p4
        # set-size cost of PAC
        sz = agg.pivot_table(index=["data_id", "model"], columns="method", values="size_novel")
        S["size_ratio_pac_vs_mcp_median"] = float((sz["PAC_MCP"] / sz["MCP"]).replace([np.inf], np.nan).median())
        S["size_ratio_mcp_vs_scp_median"] = float((sz["MCP"] / sz["SCP"]).replace([np.inf], np.nan).median())
        # normalized score (regression)
        nr = P[P.score == "normres"].groupby(["data_id", "name", "model", "method"]).cov_novel.mean().reset_index()
        if len(nr):
            S["normres"] = [dict(learner=m, method=me, n=int(len(g)), median_gap=float((g.cov_novel - 0.9).median()),
                                 worst=float((g.cov_novel - 0.9).min()))
                            for (m, me), g in nr.groupby(["model", "method"])]
        # holm over primary tests
        prim = {"P1_rf": next(x for x in S["P1_P2_P5"] if x["learner"] == "rf").get("p_gstar_one_sided", np.nan),
                "P4_rf": next(x for x in S["P4"] if x["learner"] == "rf")["p_pac_lower"]}
        p3rf = next(x for x in p3 if x["learner"] == "rf" and x["method"] == "MCP")
        S["P3_rf_mcp_noninferior"] = p3rf["noninferior"]
        keys = list(prim)
        adj = holm([prim[k] if prim[k] == prim[k] else 1.0 for k in keys])
        S["holm_primary"] = dict(zip(keys, map(float, adj)))
        scp.to_csv(os.path.join(T, "prospective_scp_purity.csv"), index=False)
        _fig_purity(scp, os.path.join(R, "purity_retrospective.csv"), F)
    # ---------------- near-duplicates
    nf = glob.glob(os.path.join(R, "neardup", "neardup_*.csv"))
    if nf:
        N = pd.concat([pd.read_csv(f) for f in nf], ignore_index=True)
        g = N.groupby(["task", "data_id", "model", "sigma", "method"]).cov_truly_new.mean().reset_index()
        g["gap"] = g.cov_truly_new - (1 - A)
        summ = g.groupby(["task", "model", "sigma", "method"]).gap.median().unstack("method").reset_index()
        det = N.groupby(["task", "sigma"]).key_detect_rate.median().reset_index()
        summ.to_csv(os.path.join(T, "neardup_summary.csv"), index=False)
        S["neardup"] = {"n_datasets": int(N.data_id.nunique()), "summary": summ.round(4).to_dict("records"),
                        "key_detect": det.round(4).to_dict("records")}
        _fig_neardup(g, F)
    json.dump(S, open(os.path.join(R, "statistics_reinforcement.json"), "w"), indent=1, default=str)
    return S


def _fig_purity(scp, retro_path, F):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .figures import MM, _save
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 70 * MM), sharey=True)
    sets = []
    if os.path.exists(retro_path):
        r = pd.read_csv(retro_path)
        sets.append(("(a) Retrospective: v1 suites + external (RF)", r[(r.model == "rf") & (r.pi >= 0.01)]))
    sets.append(("(b) Prospective: unseen suites (RF)", scp[scp.model == "rf"]))
    for ax, (title, q) in zip(axs, sets):
        lo = min(-0.5, q.g_star.min() - 0.02, q.gap_scp.min() - 0.02)
        ax.plot([lo, 0.02], [lo, 0.02], color=INK2, ls="--", lw=0.8, label="Observed = bound")
        ax.fill_between([lo, 0.02], [lo - 0.02, 0.0], [lo, 0.02], color="#e4e3df", alpha=0.6, lw=0)
        ax.scatter(q.g_star, q.gap_scp, s=12, color=C[0], edgecolor="white", linewidth=0.4, zorder=3)
        ax.axhline(0, color=INK, lw=0.8)
        ax.set_xlabel("Purity-adjusted bound g* = −απ$_P$/(1 − π$_P$) (no model)")
        ax.set_title(title, loc="left")
        ax.grid(True)
    axs[0].set_ylabel("Observed novel-record gap (split CP)")
    axs[0].legend(frameon=False, loc="upper left")
    fig.tight_layout()
    _save(fig, F, "Fig_purity")


def _fig_neardup(g, F):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .figures import MM, _save
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 62 * MM), sharey=True)
    labels = {"SCP": "Split CP", "MCP_exact": "Novelty-Mondrian (exact key)", "DCP": "Distance-Mondrian",
              "MCP_oracle": "Mondrian on true record identity (oracle)"}
    for ax, task in zip(axs, ["classification", "regression"]):
        for i, (meth, lab) in enumerate(labels.items()):
            q = g[(g.task == task) & (g.method == meth)].groupby("sigma").gap.median()
            x = np.arange(len(q))
            ax.plot(x, q.values, marker="o", ms=3.5, color=C[i], label=lab)
        ax.axhline(0, color=INK, lw=0.8)
        ax.set_xticks(range(4))
        ax.set_xticklabels(["0 (exact)", "0.001", "0.01", "0.1"])
        ax.set_xlabel("Jitter of copied records (× feature SD)")
        ax.set_title(f"({'a' if task == 'classification' else 'b'}) {task.capitalize()}", loc="left")
        ax.grid(True)
    axs[0].set_ylabel("Median coverage gap on truly new records")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    _save(fig, F, "Fig_neardup")
