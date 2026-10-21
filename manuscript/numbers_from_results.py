"""Every number quoted in the manuscript is computed here from results/ (no hand-typed results)."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

LBL = {"logreg": "LR", "rf": "RF", "lgbm": "LightGBM", "knn": "k-NN", "mlp": "MLP", "cqr": "CQR"}


def pct(x, d=1):
    return f"{100 * x:.{d}f}"


def f3(x):
    return f"{x:.3f}"


def signed_pp(x, d=1):
    return f"{100 * x:+.{d}f}".replace("-", "−")


def pval(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "n/a"
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def compute_numbers(res):
    S = json.load(open(os.path.join(res, "statistics.json")))
    T = os.path.join(res, "tables")
    n = {}
    rq1 = S["rq1"]
    aud = pd.read_csv(os.path.join(T, "T1_audit.csv"))
    n["n_cls"] = rq1["n_by_task"]["classification"]
    n["n_reg"] = rq1["n_by_task"]["regression"]
    n["n_total"] = rq1["n_datasets"]
    n["n_subsampled"] = len(rq1["subsampled"])
    n["n_any_dup"] = rq1["n_with_any_duplicate"]
    n["n_dup_ge1"] = rq1["n_dup_row_frac_ge_0.01"]
    n["n_dup_ge30"] = rq1["n_dup_row_frac_ge_0.30"]
    n["n_conflict"] = rq1["n_conflicting"]
    n["exp_mae"] = f"{rq1['pred_vs_obs_exposure_mae']:.4f}"
    n["exp_maxerr"] = f"{rq1['pred_vs_obs_exposure_max_abs_err']:.3f}"
    n["exp_r"] = f"{rq1['pred_vs_obs_pearson']:.4f}"
    sets = rq1["sets"]
    n["n_dup_cls"] = sets["DUP"]["classification"]
    n["n_dup_reg"] = sets["DUP"]["regression"]
    n["n_dup"] = n["n_dup_cls"] + n["n_dup_reg"]
    n["n_clean_cls"] = sets["CLEAN"]["classification"]
    n["n_clean_reg"] = sets["CLEAN"]["regression"]
    n["n_low"] = sets["LOW"]["classification"] + sets["LOW"]["regression"]
    dup = aud[aud.set == "DUP"]
    n["dup_exposure_median"] = f3(dup.pred_exposure.median())
    n["dup_exposure_max"] = f3(dup.pred_exposure.max())
    n["n_dup_exposure_ge01"] = int((dup.pred_exposure >= 0.1).sum())
    n["n_dup_exposure_ge03"] = int((dup.pred_exposure >= 0.3).sum())

    M = pd.DataFrame(S["main_alpha_0.1"])
    n["h1_gap_median_min"] = signed_pp(M.scp_gap_median.min())
    n["h1_gap_median_max"] = signed_pp(M.scp_gap_median.max())
    Mx = M[~((M.model == "knn") & (M.score == "lac"))]
    n["h1x_gap_median_min"] = signed_pp(Mx.scp_gap_median.min())
    n["h1x_gap_median_max"] = signed_pp(Mx.scp_gap_median.max())
    n["h1_min_p_holm"] = pval(M.p_H1_holm.min())
    n["h1_n_sig"] = int((M.p_H1_holm < 0.05).sum())
    n["h1_worst_gap"] = signed_pp(M.scp_gap_min.min())
    n["h1_worst_gap_cls"] = signed_pp(M[M.task == "classification"].scp_gap_min.min())
    n["h1_worst_gap_reg"] = signed_pp(M[M.task == "regression"].scp_gap_min.min())
    n["h1_share_lt1_range"] = f"{pct(M.share_gap_lt_minus001.min(), 0)}–{pct(M.share_gap_lt_minus001.max(), 0)}"
    sp = M.dropna(subset=["spearman_exposure_gap"])
    n["h1a_n_neg_sig"] = int(((sp.spearman_exposure_gap < 0) & (sp.p_spearman < 0.05)).sum())
    n["h1a_rho_range"] = f"{sp.spearman_exposure_gap.min():.2f} to {sp.spearman_exposure_gap.max():.2f}".replace("-", "−")
    n["h2_mcp_median_range"] = f"{signed_pp(M.mcp_gap_median.min())} to {signed_pp(M.mcp_gap_median.max())}"
    n["h2_mcp_cilo_min"] = signed_pp(M.mcp_gap_ci_lo.min())
    n["h2_noninf_all"] = "all" if (M.mcp_gap_ci_lo > -0.01).all() else f"{int((M.mcp_gap_ci_lo > -0.01).sum())} of {len(M)}"
    n["h2_n_sig"] = int((M.p_H2_holm < 0.05).sum())
    n["h2_fallbacks"] = int(M.mcp_novel_fallback_datasets.sum())
    n["h3_novel_ratio_range"] = f"{M.size_ratio_novel_median.min():.3f}–{M.size_ratio_novel_median.max():.3f}"
    n["h3_all_ratio_range"] = f"{M.size_ratio_all_median.min():.3f}–{M.size_ratio_all_median.max():.3f}"
    n["n_families"] = len(M)
    n["h3_novel_max_pct"] = f"{100 * (M.size_ratio_novel_median.max() - 1):.1f}"
    knn = M[(M.model == "knn") & (M.score == "lac")].iloc[0]
    n["knn_lac_novel_median"] = f3(knn.scp_novel_cov_median)

    # per-family table for the manuscript (Table 2)
    rows = []
    for _, r in M.iterrows():
        rows.append(f"| {r.task[:5].capitalize()}. | {LBL[r.model]} | {r.score.upper() if r.score != 'absres' else '|res|'} | "
                    f"{r.n_datasets} | {signed_pp(r.scp_gap_median, 2)} [{signed_pp(r.scp_gap_ci_lo, 2)}, {signed_pp(r.scp_gap_ci_hi, 2)}] | "
                    f"{signed_pp(r.scp_gap_min, 1)} | {pval(r.p_H1_holm)} | {r.spearman_exposure_gap:.2f}".replace("-", "−")
                    + f" | {signed_pp(r.mcp_gap_median, 2)} [{signed_pp(r.mcp_gap_ci_lo, 2)}, {signed_pp(r.mcp_gap_ci_hi, 2)}] | "
                    f"{pval(r.p_H2_holm)} | {r.size_ratio_novel_median:.3f} |")
    n["table2_rows"] = "\n".join(rows)

    # secondary alphas
    for a in ("0.05", "0.2"):
        k = f"main_alpha_{a}"
        if k in S:
            Ma = pd.DataFrame(S[k])
            n[f"a{a}_gap_median_range"] = f"{signed_pp(Ma.scp_gap_median.min())} to {signed_pp(Ma.scp_gap_median.max())}"
            n[f"a{a}_worst"] = signed_pp(Ma.scp_gap_min.min())
            n[f"a{a}_mcp_cilo_min"] = signed_pp(Ma.mcp_gap_ci_lo.min())
            n[f"a{a}_n_sig"] = int((Ma.p_H1_holm < 0.05).sum())

    E = S["exploratory"]
    n["x_pairs"] = E["n_pairs"]
    n["x_pairs_lt2"] = E["pairs_gap_lt_m002"]
    n["x_pairs_lt5"] = E["pairs_gap_lt_m005"]
    n["x_ds_lt2"] = E["datasets_any_gap_lt_m002"]
    n["x_ds_lt5"] = E["datasets_any_gap_lt_m005"]
    n["x_worst"] = signed_pp(E["worst_gap"])
    n["x_worst_mcp"] = signed_pp(E["worst_mcp_gap"])
    n["x_mcp_pairs_lt2"] = E["mcp_pairs_gap_lt_m002"]
    n["x_rho_mech"] = f"{E['spearman_seen_excess_term_vs_gap'][0]:.2f}"
    n["x_marginal"] = f"{100 * E['median_abs_marginal_term']:.1f}"
    X1 = pd.read_csv(os.path.join(T, "X1_exploratory_pairs.csv"))
    for did, key in [(44966, "sf"), (44984, "cps"), (1067, "kc1")]:
        q = X1[(X1.data_id == did) & X1.score.isin(["lac", "absres"])]
        if len(q):
            nov = q.gap + 0.9
            n[f"{key}_novel_range"] = f"{nov.min():.2f}–{nov.max():.2f}"
            n[f"{key}_seen_range"] = f"{q.cov_seen.min():.2f}–{q.cov_seen.max():.2f}"
    n["x_rho_exp"] = f"{E['spearman_exposure_vs_gap_pooled'][0]:.2f}".replace("-", "−")
    st = pd.DataFrame(E["strata"])
    for lab, key in [("pi<0.1", "lo"), ("0.1<=pi<0.3", "mid"), ("pi>=0.3", "hi")]:
        q = st[st.stratum == lab]
        if len(q):
            n[f"x_{key}_pairs"] = int(q.n_pairs.sum())
            n[f"x_{key}_ds"] = int(q.n_datasets.max())
            w = q.n_pairs / q.n_pairs.sum()
            n[f"x_{key}_share2"] = pct(float((q.share_lt_m002 * w).sum()), 0)
            n[f"x_{key}_share5"] = pct(float((q.share_lt_m005 * w).sum()), 0)
            n[f"x_{key}_mcp_share2"] = pct(float((q.mcp_share_lt_m002 * w).sum()), 0)
            n[f"x_{key}_min"] = signed_pp(q.gap_min.min())
    # stratum table
    srows = []
    for _, r in st.iterrows():
        srows.append(f"| {r.stratum.replace('pi', 'π').replace('<=', '≤')} | {r.score if r.score != 'absres' else '|res|'} | {r.n_datasets} | {r.n_pairs} | "
                     f"{signed_pp(r.gap_median, 2)} | {signed_pp(r.gap_p10, 1)} | {signed_pp(r.gap_min, 1)} | {pct(r.share_lt_m002, 0)} | "
                     f"{signed_pp(r.mcp_gap_median, 2)} | {signed_pp(r.mcp_gap_min, 1)} |")
    n["table3_rows"] = "\n".join(srows)

    # Friedman
    F = S["H1b_friedman"]
    for k, v in F.items():
        n[f"fr_{k}_chi2"] = f"{v['chi2']:.1f}"
        n[f"fr_{k}_p"] = pval(v["p"])
        n[f"fr_{k}_n"] = v["n"]

    # group split
    G = pd.DataFrame(S["H6_group_split"])
    n["h6_median_range"] = f"{f3(G.g_cov_median.min())}–{f3(G.g_cov_median.max())}"
    g2 = G[~((G.model == "knn") & (G.score == "lac"))]
    n["h6_median_range_noknn"] = f"{f3(g2.g_cov_median.min())}–{f3(g2.g_cov_median.max())}"
    n["h6_noninf"] = "all" if G.noninferior_0_01.all() else f"{int(G.noninferior_0_01.sum())} of {len(G)}"

    # null control
    N = pd.DataFrame(S["null_control"])
    n2 = N[~((N.model == "knn") & (N.score == "lac"))]
    n["null_median_range"] = f"{f3(n2.scp_cov_median.min())}–{f3(n2.scp_cov_median.max())}"
    n["null_knn_lac"] = f3(N[(N.model == "knn") & (N.score == "lac")].scp_cov_median.iloc[0])
    n["null_maxdiff"] = f"{N.max_abs_mcp_minus_scp.max():.3g}"

    # calibration
    Cb = pd.DataFrame(S["H4_calibration"])
    n["cal_acc_seen_range"] = f"{f3(Cb.acc_seen_median.min())}–{f3(Cb.acc_seen_median.max())}"
    n["cal_acc_novel_range"] = f"{f3(Cb.acc_novel_median.min())}–{f3(Cb.acc_novel_median.max())}"
    n["cal_oc_n_sig"] = int((Cb.p_oc_holm < 0.05).sum())
    n["cal_ece_n_sig"] = int((Cb.p_ece_holm < 0.05).sum())
    n["cal_oc_diff_range"] = f"{signed_pp(Cb.oc_diff_median.min(), 2)} to {signed_pp(Cb.oc_diff_median.max(), 2)}"
    n["cal_ece_diff_range"] = f"{signed_pp(Cb.ece_diff_median.min(), 2)} to {signed_pp(Cb.ece_diff_median.max(), 2)}"
    crow = []
    for _, r in Cb.iterrows():
        crow.append(f"| {LBL[r.model]} | {r.n} | {f3(r.acc_seen_median)} | {f3(r.acc_novel_median)} | {signed_pp(r.oc_all_median, 2)} | "
                    f"{signed_pp(r.oc_novel_median, 2)} | {pval(r.p_oc_holm)} | {pct(r.ece_sizematched_median, 2)} | {pct(r.ece_novel_median, 2)} | {pval(r.p_ece_holm)} |")
    n["table4_rows"] = "\n".join(crow)

    # injection / capacity
    for key, lab in [("D_injection", "inj"), ("F_capacity", "cap")]:
        if key not in S:
            continue
        D = S[key]
        for k, v in D.items():
            n[f"{lab}_{k}_n"] = v["n_datasets"]
            n[f"{lab}_{k}_rho"] = f"{v['median_spearman']:.2f}".replace("-", "−")
            n[f"{lab}_{k}_p"] = pval(v["p_spearman_lt0"])
            bl = pd.DataFrame(v["by_level"])
            xv = "rate" if lab == "inj" else "level"
            for _, r in bl.iterrows():
                tag = f"{r[xv]:g}".replace(".", "p")
                n[f"{lab}_{k}_{tag}_gap"] = signed_pp(r.gap)
                n[f"{lab}_{k}_{tag}_mcp"] = signed_pp(r.mcp_gap)
                n[f"{lab}_{k}_{tag}_lim"] = signed_pp(r.limit_gap)
                n[f"{lab}_{k}_{tag}_pi"] = f3(r.exposure)
                n[f"{lab}_{k}_{tag}_seen"] = f3(r.cov_seen)
        n[f"{lab}_n_ds"] = max(v["n_datasets"] for v in D.values())
    if "D_injection" in S:
        ps = [v["p_spearman_lt0"] for v in S["D_injection"].values()]
        n["inj_all_sig"] = "all" if all(p < 0.05 for p in ps if p == p) else f"{sum(p < 0.05 for p in ps)} of {len(ps)}"
    # exploratory distance bins
    if "E_distance_bins" in S:
        Db = pd.DataFrame(S["E_distance_bins"])
        for task in ("classification", "regression"):
            q = Db[(Db.task == task) & (Db.method == "SCP")].set_index("bin")["median"]
            if len(q):
                n[f"dist_{task}_q1"] = f3(q.get(0, np.nan))
                n[f"dist_{task}_q5"] = f3(q.get(4, np.nan))
                n[f"dist_{task}_seen"] = f3(q.get(5, np.nan))
            q = Db[(Db.task == task) & (Db.method == "DCP")].set_index("bin")["median"]
            if len(q):
                n[f"dcp_{task}_min"] = f3(q.min())
    return n


if __name__ == "__main__":
    import sys
    print(json.dumps(compute_numbers(sys.argv[1]), indent=1)[:4000])
