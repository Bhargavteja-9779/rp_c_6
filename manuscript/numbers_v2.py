"""Numbers for the revised manuscript (v2). Extends the v1 number set with the case studies and
the reinforcement-cycle analyses. Every value is read from a result file."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

from numbers_from_results import compute_numbers, pval, signed_pp


def p1(x):
    return f"{100 * x:.1f}"


def compute_numbers_v2(res):
    n = compute_numbers(res)
    R = os.path.join(res, "reinforcement")
    cs = pd.read_csv(os.path.join(R, "tables", "case_studies.csv"))
    rf = cs[cs.model == "rf"].set_index("name")
    for nm, key in [("mc1", "mc1"), ("pc2", "pc2"), ("kc1", "kc1"), ("KDDCup99", "kdd"), ("PhishingWebsites", "phish"),
                    ("kc3", "kc3"), ("mw1", "mw1"), ("kc2", "kc2"), ("pc1", "pc1"), ("pc3", "pc3"),
                    ("pc4", "pc4"), ("jm1", "jm1")]:
        r = rf.loc[nm]
        n[f"cs_{key}_reported"] = p1(r.reported_cov)
        n[f"cs_{key}_new"] = p1(r.new_cov_standard)
        n[f"cs_{key}_fixed"] = p1(r.new_cov_fixed)
        n[f"cs_{key}_pi"] = f"{100 * r.pi:.0f}%"
        n[f"cs_{key}_pred"] = signed_pp(r.predicted_gap)
        n[f"cs_{key}_size_std"] = f"{r.size_new_standard:.2f}"
        n[f"cs_{key}_size_fix"] = f"{r.size_new_fixed:.2f}"
    # case-study table (RF and LightGBM)
    rows = []
    for _, r in cs[cs.model.isin(["rf", "lgbm"])].sort_values(["application", "pi"], ascending=[True, False]).iterrows():
        rows.append(f"| {r.application} | {r['name']} | {'RF' if r.model == 'rf' else 'LightGBM'} | {r.pi:.2f} | "
                    f"{signed_pp(r.predicted_gap)} | {p1(r.reported_cov)} | {p1(r.new_cov_standard)} | {p1(r.new_cov_fixed)} | "
                    f"{r.size_new_standard:.2f} → {r.size_new_fixed:.2f} |")
    n["case_table_rows"] = "\n".join(rows)
    flag = cs[(cs.model == "rf") & (cs.predicted_gap < -0.02)]
    noflag = cs[(cs.model == "rf") & (cs.predicted_gap >= -0.02)]
    n["cs_n_flag"] = len(flag)
    n["cs_n_noflag"] = len(noflag)
    n["cs_flag_new_range"] = f"{p1(flag.new_cov_standard.min())}–{p1(flag.new_cov_standard.max())}"
    n["cs_flag_fixed_range"] = f"{p1(flag.new_cov_fixed.min())}–{p1(flag.new_cov_fixed.max())}"
    safe = rf.loc[["pc1", "pc3", "pc4", "jm1", "mw1"]]
    n["cs_safe_range"] = f"{p1(safe.new_cov_standard.min())}–{p1(safe.new_cov_standard.max())}"
    n["cs_noflag_new_range"] = f"{p1(noflag.new_cov_standard.min())}–{p1(noflag.new_cov_standard.max())}"

    # v1 ranges given as proportions "0.73–0.79" -> percentages "73–79%" for the plain-language text
    for k in ("sf_novel_range", "cps_novel_range", "h6_median_range_noknn"):
        a, b = (float(x) for x in str(n[k]).split("–"))
        n[k + "_pct"] = f"{100 * a:.0f}–{100 * b:.0f}%" if k != "h6_median_range_noknn" else f"{100 * a:.1f}–{100 * b:.1f}%"
    S = json.load(open(os.path.join(R, "statistics_reinforcement.json")))
    # retrospective purity
    for x in S.get("retrospective", []):
        m = x["learner"]
        n[f"rp_{m}_n"] = x["n"]
        n[f"rp_{m}_rho"] = f"{x['rho_gstar']:.2f}"
        n[f"rp_{m}_rho_pi"] = f"{x['rho_gpi']:.2f}"
        n[f"rp_{m}_above"] = p1(x["share_above_bound"])
        n[f"rp_{m}_ratio"] = f"{x.get('median_ratio_obs_to_gstar', float('nan')):.2f}"
        lo, hi = x["rho_diff_ci"]
        n[f"rp_{m}_diffci"] = f"{lo:.2f} to {hi:.2f}".replace("-", "−")
    for x in S.get("retrospective_injection", []):
        n[f"rpi_{x['learner']}_rho"] = f"{x['rho_gstar']:.2f}"
        n[f"rpi_{x['learner']}_ratio"] = f"{x['median_ratio_at_rate1']:.2f}"
    # prospective
    if "P1_P2_P5" in S:
        n["pr_n"] = S["prospective_n_datasets"]
        n["pr_n_cls"] = S["prospective_tasks"].get("classification", 0)
        n["pr_n_reg"] = S["prospective_tasks"].get("regression", 0)
        for x in S["P1_P2_P5"]:
            m = x["learner"]
            if "rho_gstar" not in x:
                continue
            n[f"pr_{m}_rho"] = f"{x['rho_gstar']:.2f}"
            n[f"pr_{m}_p"] = pval(x["p_gstar_one_sided"])
            n[f"pr_{m}_rho_pi"] = f"{x['rho_gpi']:.2f}"
            lo, hi = x["rho_diff_ci"]
            n[f"pr_{m}_diffci"] = f"{lo:.2f} to {hi:.2f}".replace("-", "−")
            n[f"pr_{m}_above"] = p1(x["share_above_bound"])
            n[f"pr_{m}_above_ci"] = f"{p1(x['share_above_ci'][0])}–{p1(x['share_above_ci'][1])}"
            n[f"pr_{m}_ratio"] = f"{x['median_ratio_obs_to_gstar']:.2f}" if x["median_ratio_obs_to_gstar"] == x["median_ratio_obs_to_gstar"] else "n/a"
            n[f"pr_{m}_nviol"] = len(x.get("violations", []))
        for x in S["P3"]:
            k = f"pr3_{x['learner']}_{x['method']}"
            n[k + "_med"] = signed_pp(x["median_gap"])
            n[k + "_lo"] = signed_pp(x["ci_lo"])
            n[k + "_worst"] = signed_pp(x["worst"])
            n[k + "_bad"] = p1(x["mean_bad_split_rate"])
            n[k + "_ni"] = "yes" if x["noninferior"] else "no"
            n[k + "_fb"] = p1(x["fallback_rate"])
        for x in S["P4"]:
            n[f"pr4_{x['learner']}_mcp"] = p1(x["mcp_bad_mean"])
            n[f"pr4_{x['learner']}_pac"] = p1(x["pac_bad_mean"])
            n[f"pr4_{x['learner']}_p"] = pval(x["p_pac_lower"])
        n["pr_size_pac"] = f"{S['size_ratio_pac_vs_mcp_median']:.2f}"
        n["pr_size_mcp"] = f"{S['size_ratio_mcp_vs_scp_median']:.2f}"
        n["pr_holm_P1"] = pval(S["holm_primary"]["P1_rf"])
        n["pr_holm_P4"] = pval(S["holm_primary"]["P4_rf"])
        for x in S.get("normres", []):
            n[f"prn_{x['learner']}_{x['method']}_med"] = signed_pp(x["median_gap"])
            n[f"prn_{x['learner']}_{x['method']}_worst"] = signed_pp(x["worst"])
        # prospective table
        T = pd.read_csv(os.path.join(R, "tables", "prospective_per_dataset.csv"))
        rows = []
        for (did, name, task), g in T[T.model == "rf"].groupby(["data_id", "name", "task"]):
            gg = g.set_index("method")
            pi_p = gg.pi_p.iloc[0]
            gstar = -0.1 * pi_p / (1 - pi_p) if pi_p < 0.9 else -0.9
            cell = lambda m: p1(gg.loc[m, "cov_novel"]) if m in gg.index else "–"
            rows.append((gstar, f"| {name} | {task[:5]}. | {gg.pi.iloc[0]:.2f} | {pi_p:.2f} | {signed_pp(gstar)} | "
                                f"{cell('SCP')} | {cell('MCP')} | {cell('PAC_MCP')} | {cell('DCP')} |"))
        n["pr_table_rows"] = "\n".join(r for _, r in sorted(rows, key=lambda t: t[0]))
        # screening view: does a predicted gap worse than -2 pp flag the data sets that really fall short?
        sp = pd.read_csv(os.path.join(R, "tables", "prospective_scp_purity.csv"))
        lab = {"rf": "random forest", "lgbm": "LightGBM", "logreg": "linear model"}
        for pred in ("g_star", "g_pi"):
            tag = "gs" if pred == "g_star" else "gp"
            q = sp[sp.model == "rf"]
            n[f"pr_{tag}_nflag"] = int((q[pred] < -0.02).sum())
            for m in ("rf", "lgbm", "logreg"):
                q = sp[sp.model == m]
                fl, un = q[q[pred] < -0.02], q[q[pred] >= -0.02]
                n[f"pr_{tag}_{m}_hit"] = int((fl.gap_scp < -0.02).sum())
                n[f"pr_{tag}_{m}_miss"] = int((un.gap_scp < -0.02).sum())
                n[f"pr_{tag}_{m}_unflag_worst"] = signed_pp(un.gap_scp.min())
        # the rule stated in the Discussion before the fresh results existed: g* >= -2 pp and exposure < 0.1
        q = sp[(sp.g_star >= -0.02) & (sp.pi < 0.1)]
        n["pr_rule_n"] = int(q.data_id.nunique())
        n["pr_rule_worst"] = signed_pp(q.gap_scp.min())
        get = lambda name, m, col: sp[(sp.name == name) & (sp.model == m)][col].iloc[0]
        for key, name in [("sup", "analcatdata_supreme"), ("bf", "black_friday"), ("sc", "seattlecrime6"),
                          ("air", "airlines"), ("cond", "superconduct"), ("wine", "wine_quality")]:
            n[f"pr_{key}_pi"] = f"{100 * get(name, 'rf', 'pi'):.0f}%"
            n[f"pr_{key}_pip"] = f"{100 * get(name, 'rf', 'pi_p'):.0f}%"
            n[f"pr_{key}_gs"] = signed_pp(get(name, "rf", "g_star"))
            n[f"pr_{key}_gp"] = signed_pp(get(name, "rf", "g_pi"))
            for m in ("rf", "lgbm", "logreg"):
                n[f"pr_{key}_{m}_gap"] = signed_pp(get(name, m, "gap_scp"))
        T2 = pd.read_csv(os.path.join(R, "tables", "prospective_per_dataset.csv"))
        fb = T2[(T2.method == "MCP") & (T2.fallback > 0)]
        n["pr_fb_names"] = ", ".join(sorted(fb.name.unique()))
        n["pr_fb_rate"] = p1(fb.fallback.max()) if len(fb) else "0"
    # near-duplicates
    if "neardup" in S:
        nd = pd.DataFrame(S["neardup"]["summary"])
        n["nd_n"] = S["neardup"]["n_datasets"]
        for task in ("classification", "regression"):
            for sig in (0.0, 0.001, 0.01, 0.1):
                q = nd[(nd.task == task) & (nd.model == "rf") & np.isclose(nd.sigma, sig)]
                if len(q):
                    q = q.iloc[0]
                    tag = f"{task[:3]}_{str(sig).replace('.', 'p')}"
                    for meth in ("SCP", "MCP_exact", "DCP", "MCP_oracle"):
                        if meth in q and q[meth] == q[meth]:
                            n[f"nd_{tag}_{meth}"] = signed_pp(q[meth])
        det = pd.DataFrame(S["neardup"]["key_detect"])
        for task in ("classification", "regression"):
            q = det[(det.task == task) & (det.sigma > 0)]
            n[f"nd_detect_{task[:3]}"] = p1(q.key_detect_rate.max()) if len(q) else "n/a"
    return n
