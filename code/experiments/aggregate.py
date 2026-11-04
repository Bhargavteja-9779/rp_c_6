"""Aggregate every result file into LaTeX: paper/tables/macros.tex (one \\newcommand per number) and
paper/tables/tab_*.tex (every table). The manuscript uses only these macros and tables, never typed
numbers. Re-running this script after any experiment updates the whole paper.

Macro names: the key of the number with every digit spelled out, CamelCased and prefixed with N, e.g.
cs_mc1_new -> \\NCsMcOneNew. Counts below ten also get a word form with the suffix W (\\NScTwoPosW = "nine").
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "manuscript"))
from numbers_v2 import compute_numbers_v2  # noqa: E402
from numbers_from_results import signed_pp  # noqa: E402

RES = os.path.join(ROOT, "results")
R = os.path.join(RES, "reinforcement")
TAB = os.path.join(ROOT, "paper", "tables")
DIG = "Zero One Two Three Four Five Six Seven Eight Nine".split()
WORDS = "zero one two three four five six seven eight nine".split()


def macro_name(key: str) -> str:
    out = []
    for tok in re.split(r"[^A-Za-z0-9]+", key):
        if not tok:
            continue
        s = "".join(DIG[int(c)] if c.isdigit() else c for c in tok)
        out.append(s[0].upper() + s[1:])
    return "N" + "".join(out)


def tex(v) -> str:
    s = str(v)
    rep = [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
           ("−", r"\ensuremath{-}"), ("–", "--"), ("→", r"\ensuremath{\to}"), ("≥", r"\ensuremath{\geq}"),
           ("≤", r"\ensuremath{\leq}"), ("<", r"\ensuremath{<}"), (">", r"\ensuremath{>}"), ("×", r"\ensuremath{\times}"),
           ("π", r"\ensuremath{\pi}"), ("…", r"\ldots{}"), ("'", "'")]
    for a, b in rep:
        s = s.replace(a, b)
    return s


def pct(x, d=1):
    return f"{100 * x:.{d}f}"


# ------------------------------------------------------------------ extra numbers (E10–E14, ablation)
def extra_numbers(n):
    p = os.path.join(RES, "e10_planted_leak", "planted_leak.json")
    if os.path.exists(p):
        s = json.load(open(p))["summary"]
        n.update(leak_n=s["n_datasets"], leak_planted=f"{s['planted_total']:,}", leak_recall=pct(s["exact_recall_min"], 0),
                 leak_fp=s["exact_false_pos"] + s["clean_false_pos"], leak_jitter_recall=pct(s["jitter_recall_max"], 0))
    p = os.path.join(RES, "e11_sampling_noise", "noise_check.json")
    if os.path.exists(p):
        S = pd.DataFrame(json.load(open(p))["summary"])
        for _, r in S.iterrows():
            k = f"noise_{r.method}_{r.model}"
            n[k + "_obs"] = int(r.observed)
            n[k + "_exp"] = f"{r.expected:.0f}"
            n[k + "_ratio"] = f"{r.ratio:.2f}"
            n[k + "_p"] = f"{r.p_excess:.3f}" if r.p_excess >= 0.001 else "< 0.001"
            n[k + "_n"] = int(r.n_splits)
    p = os.path.join(RES, "e12_qualitative", "class_conditional.json")
    if os.path.exists(p):
        C = pd.DataFrame(json.load(open(p)))
        key = {"standard": "std", "fix (seen/new)": "fix", "fix by class (seen/new x label)": "cls"}
        for _, r in C.iterrows():
            k = f"cc_{key[r.method]}_{'def' if r.label == 'defect' else 'ok'}"
            n[k + "_cov"] = pct(r.coverage)
            n[k + "_size"] = f"{r['size']:.2f}"
            n[k + "_n"] = f"{int(r.n_total):,}"
    p = os.path.join(RES, "e12_qualitative", "examples.json")
    if os.path.exists(p):
        E = json.load(open(p))
        n["ex_q_std"] = f"{E['thresholds']['standard']:.3f}"
        n["ex_q_new"] = f"{E['thresholds']['fixed_new']:.3f}"
        n["ex_q_seen"] = f"{E['thresholds']['fixed_seen']:.3f}"
    p = os.path.join(RES, "e13_cost", "cost.json")
    if os.path.exists(p):
        C = json.load(open(p))
        hw = C["hardware"]
        n.update(hw_cpu=hw["cpu"], hw_ncpu=hw["logical_cpus"], hw_ram=f"{hw['ram_gb']:.0f}", hw_python=hw["python"])
        rows = C["rows"]
        n["cost_check_max"] = f"{max(r['check_s'] for r in rows):.2f}"
        n["cost_check_mem_max"] = f"{max(r['check_peak_mb'] for r in rows):.0f}"
        n["cost_cal_exact_max"] = f"{max(r['exact_calibrate_s'] for r in rows):.2f}"
        n["cost_cal_std_max"] = f"{max(r['standard_calibrate_s'] for r in rows):.2f}"
        n["cost_fit_max"] = f"{max(r['fit_s'] for r in rows):.2f}"
    p = os.path.join(RES, "e14_tool_validation", "tool_validation.json")
    if os.path.exists(p):
        s = json.load(open(p))["summary"]
        n.update(tv_n=s["n"], tv_exp_diff_exp=int(np.ceil(np.log10(max(s["exposure_max_absdiff"], 1e-300)))),
                 tv_flag=s["flag_agreement"], tv_std_2se=s["within_2se_std"], tv_fix_2se=s["within_2se_fix"],
                 tv_med_std=f"{100 * s['median_absdiff_std']:.1f}", tv_med_fix=f"{100 * s['median_absdiff_fix']:.1f}",
                 tv_max_fix=f"{100 * s['max_absdiff_fix']:.1f}")
    # ablation of the check: which flag rule catches the shortfalls (pooled waves 1 and 2)?
    p = os.path.join(R, "tables", "screening.csv")
    if os.path.exists(p):
        sc = pd.read_csv(p)
        sc["g_pi"] = [-0.1 * x / (1 - x) if x < 0.9 else -0.9 for x in sc.pred_exposure]
        rules = {"expo": (sc.pred_exposure >= 0.10) | (sc.g_pi < -0.02), "pure": sc.g_star < -0.02,
                 "comb": sc.flag.astype(bool)}
        pos = sc.positive.astype(bool)
        for k, f in rules.items():
            n[f"abl_{k}_flag"] = int(f.sum())
            n[f"abl_{k}_sens"] = f"{int((f & pos).sum())}/{int(pos.sum())}"
            n[f"abl_{k}_spec"] = f"{int((~f & ~pos).sum())}/{int((~pos).sum())}"
            n[f"abl_{k}_fa"] = int((f & ~pos).sum())
        n["abl_npos"] = int(pos.sum())
        n["abl_nds"] = len(sc)
    # counts and extremes used in the abstract and text
    cs = pd.read_csv(os.path.join(R, "tables", "case_studies.csv"))
    n["cs_n_flag_total"] = int(cs[cs.model == "rf"].shape[0])
    S2 = json.load(open(os.path.join(R, "statistics_amendment2.json")))
    S1 = json.load(open(os.path.join(R, "statistics_reinforcement.json")))
    worst = [x["worst"] for x in S2["W2"]] + [x["worst"] for x in S1["P3"] if x["method"] == "MCP"]
    n["w2_worst_fix_abs"] = f"{100 * max(abs(w) for w in worst):.1f}"
    d = pd.read_parquet(os.path.join(ROOT, "data_cache", "1056.parquet"))
    n["mc1_def_share"] = f"{100 * (d['__target__'].astype(str).str.upper() == 'TRUE').mean():.1f}"
    return n


# ------------------------------------------------------------------ tables
def write(name, body):
    open(os.path.join(TAB, f"tab_{name}.tex"), "w").write(body)


def table_cases():
    cs = pd.read_csv(os.path.join(R, "tables", "case_studies.csv"))
    cs = cs[cs.model.isin(["rf", "lgbm"])].sort_values(["application", "pi", "model"], ascending=[True, False, False])
    lines = []
    for app, g in cs.groupby("application", sort=False):
        if lines:
            lines.append(r"\addlinespace")
        lines.append(f"\\multicolumn{{8}}{{@{{}}l}}{{\\emph{{{tex(app)}}}}} \\\\")
        for _, r in g.iterrows():
            lines.append(f"{tex(r['name'])} & {'RF' if r.model == 'rf' else 'LGBM'} & {pct(r.pi, 0)} & "
                         f"{tex(signed_pp(r.predicted_gap))} & {pct(r.reported_cov)} & {pct(r.new_cov_standard)} & "
                         f"{pct(r.new_cov_fixed)} & {r.size_new_standard:.2f}\\,/\\,{r.size_new_fixed:.2f} \\\\")
    write("cases", "\n".join(lines) + "\n")


def table_remedies():
    g = pd.read_csv(os.path.join(R, "tables", "remedies_summary.csv"))
    g = g[g.model == "rf"]
    full = g[g.method == "SCP"].set_index("name").n_train
    g["share"] = g.n_train / g.name.map(full)
    names = {"SCP": "Standard (no fix)", "Dedup": "Remove repeats, then calibrate", "GSCP": "Group split",
             "MCP": r"\textbf{Seen/new calibrated separately}", "PAC_MCP": "\\quad + safety margin ($\\delta=0.1$)",
             "DCP": "Calibration by distance"}
    lines = []
    for m in ["SCP", "Dedup", "GSCP", "MCP", "PAC_MCP", "DCP"]:
        q = g[g.method == m]
        seen = "--" if m == "GSCP" else f"{pct(q.cov_seen.median())} & {q.size_seen.median():.2f}"
        if m == "GSCP":
            seen = "-- & --"
        lines.append(f"{names[m]} & {pct(q.cov_new.median())} & {pct(q.cov_new.min())} & {pct(q.empty_new.median())} & "
                     f"{seen} & {pct(q.share.median(), 0)} \\\\")
    write("remedies", "\n".join(lines) + "\n")


def table_examples():
    E = json.load(open(os.path.join(RES, "e12_qualitative", "examples.json")))
    lines = []
    rule_short = {"first seen module": "(a) first seen", "first new modules (any outcome)": "(b) first new",
                  "first new defective module": "(c) first new defective",
                  "first new module the fixed set misses": "(d) first miss of the fix"}
    for r in E["rows"]:
        tick = lambda b: r"\cmark" if b else r"\xmark"
        lines.append(f"{rule_short[r['rule']]} & {r['row']} & {'seen' if r['seen'] else 'new'} & {int(r['LOC_TOTAL'])} & "
                     f"{int(r['CYCLOMATIC_COMPLEXITY'])} & {r['true']} & {r['p_defect']:.3f} & "
                     f"{_set(r['set_standard'])} {tick(r['covered_standard'])} & "
                     f"{_set(r['set_fixed'])} {tick(r['covered_fixed'])} \\\\")
    write("examples", "\n".join(lines) + "\n")


def _set(s):
    s = s.replace("{ } (empty)", r"$\emptyset$").replace("no defect", "N").replace("defect", "D")
    return s.replace("{", r"\{").replace("}", r"\}").replace(r"\{$\emptyset$\}", r"$\emptyset$") if "emptyset" not in s else s


def table_cost():
    C = json.load(open(os.path.join(RES, "e13_cost", "cost.json")))
    lines = []
    for r in C["rows"]:
        lines.append(f"{tex(r['data'])} & {r['rows']:,} & {r['features']} & {r['check_s']:.2f} & {r['check_peak_mb']:.0f} & "
                     f"{r['fit_s']:.2f} & {r['standard_calibrate_s']:.2f} & {r['exact_calibrate_s']:.2f} & "
                     f"{r['distance_calibrate_s']:.2f} & {r['exact_predict_s']:.2f} \\\\")
    write("cost", "\n".join(lines) + "\n")


def table_wave(wave):
    sc = pd.read_csv(os.path.join(R, "tables", "screening.csv"))
    sc = sc[sc.wave == wave].sort_values("g_star")
    folder, prefix = ("prospective", "prosp") if wave == 1 else ("prospective_w2", "w2")
    P = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(R, folder, f"{prefix}_*.csv"))])
    if "error" in P:
        P = P[P.error.isna()]
    P = P[(P.model == "rf") & P.score.isin(["lac", "absres"])]
    P["data_id"] = P.data_id.astype(str)
    g = P.groupby(["data_id", "method"]).cov_novel.mean().unstack()
    lines = []
    for _, r in sc.iterrows():
        q = g.loc[str(r.data_id)] if str(r.data_id) in g.index else {}
        cell = lambda m: pct(q[m]) if m in q and q[m] == q[m] else "--"
        name = tex(r["name"]).replace(r"\_", r"\_\allowbreak{}")
        lines.append(f"{name} & {r.task[:5]}. & {pct(r.pred_exposure, 0)} & {tex(signed_pp(r.g_star))} & "
                     f"{r'\cmark' if r.flag else ''} & {cell('SCP')} & {cell('MCP')} & {cell('PAC_MCP')} & {cell('DCP')} \\\\")
    write(f"wave{wave}", "\n".join(lines) + "\n")


def table_toolval():
    T = json.load(open(os.path.join(RES, "e14_tool_validation", "tool_validation.json")))["rows"]
    lines = []
    for r in T:
        name = tex(r["name"]).replace(r"\_", r"\_\allowbreak{}")
        lines.append(f"{name} & {r['rows']:,} & {pct(r['exposure_tool'], 1)} & {tex(r['verdict_tool'].title())} & "
                     f"{pct(r['new_std_tool'])} / {pct(r['new_std_pipeline'])} & {pct(r['new_fix_tool'])} / {pct(r['new_fix_pipeline'])} \\\\")
    write("toolval", "\n".join(lines) + "\n")


def table_noise():
    S = pd.DataFrame(json.load(open(os.path.join(RES, "e11_sampling_noise", "noise_check.json")))["summary"])
    meth = {"SCP": "Standard", "MCP": "Seen/new separately", "PAC_MCP": "+ safety margin"}
    lab = {"rf": "RF", "lgbm": "LGBM", "logreg": "Linear"}
    lines = []
    for m in ["SCP", "MCP", "PAC_MCP"]:
        for mod in ["rf", "lgbm", "logreg"]:
            r = S[(S.method == m) & (S.model == mod)].iloc[0]
            p = f"{r.p_excess:.3f}" if r.p_excess >= 0.001 else r"\ensuremath{<}0.001"
            lines.append(f"{tex(meth[m]) if mod == 'rf' else ''} & {lab[mod]} & {int(r.n_splits)} & {int(r.observed)} & "
                         f"{r.expected:.1f} & {r.ratio:.2f} & {p} \\\\")
    write("noise", "\n".join(lines) + "\n")


def table_planted():
    T = pd.DataFrame(json.load(open(os.path.join(RES, "e10_planted_leak", "planted_leak.json")))["rows"])
    lines = []
    for _, r in T.iterrows():
        rec = "--" if r.planted == 0 else pct(r.recall, 0)
        lines.append(f"{tex(r['name'])} & {tex(r.plant.replace('jitter_0.001sd', 'jittered (0.1% SD)'))} & {pct(r.f, 0)} & "
                     f"{int(r.planted)} & {int(r.flagged)} & {int(r.true_pos)} & {int(r.false_pos)} & {rec} \\\\")
    write("planted", "\n".join(lines) + "\n")


def table_h1():
    t = pd.read_csv(os.path.join(RES, "tables", "T2_main_alpha0.1.csv"))
    lab = {"logreg": "LR", "rf": "RF", "lgbm": "LGBM", "knn": "kNN", "mlp": "MLP"}
    lines = []
    for _, r in t.iterrows():
        p = lambda v: (f"{v:.3f}" if v >= 0.001 else r"\ensuremath{<}0.001")
        lines.append(f"{r.task[:5]}. & {lab.get(r.model, tex(r.model))} & {tex(r.score)} & {int(r.n_datasets)} & {tex(signed_pp(r.scp_gap_median))} & "
                     f"{tex(signed_pp(r.scp_gap_min))} & {p(r.p_H1_holm)} & {tex(f'{r.spearman_exposure_gap:.2f}'.replace('-', '−'))} & "
                     f"{tex(signed_pp(r.mcp_gap_median))} & {tex(signed_pp(r.mcp_gap_ci_lo))} & {r.size_ratio_novel_median:.3f} \\\\")
    write("h1", "\n".join(lines) + "\n")


def table_selection():
    rows = []
    for wave, f in ((1, "prospective_selection.json"), (2, "prospective_selection_w2.json")):
        sel = json.load(open(os.path.join(R, f)))
        reasons = pd.Series([e["excluded"].split(":")[0] for e in sel["excluded"]]).value_counts()
        rows.append(f"\\emph{{Wave {wave}}}: pool of {sel['pool_size']} data sets & \\\\")
        for reason, k in reasons.items():
            rows.append(f"\\quad {tex(reason)} & {k} \\\\")
        rows.append(f"\\quad \\textbf{{included}} & \\textbf{{{len(sel['included'])}}} \\\\")
    write("selection", "\n".join(rows) + "\n")


def main():
    os.makedirs(TAB, exist_ok=True)
    n = extra_numbers(compute_numbers_v2(RES))
    out, names = [], {}
    for k, v in sorted(n.items()):
        if k.endswith("_rows") or k.startswith("_") or isinstance(v, (list, dict)):
            continue
        name = macro_name(k)
        if name in names and names[name] != k:
            raise SystemExit(f"macro name collision: {k} and {names[name]} -> {name}")
        names[name] = k
        out.append(f"\\newcommand{{\\{name}}}{{{tex(v)}}}  % {k}")
        if isinstance(v, (int, np.integer)) and 0 <= v < 10:
            out.append(f"\\newcommand{{\\{name}W}}{{{WORDS[int(v)]}}}  % {k} (word)")
    open(os.path.join(TAB, "macros.tex"), "w").write(
        "% Generated by code/experiments/aggregate.py from results/. Do not edit by hand.\n" + "\n".join(out) + "\n")
    json.dump({k: v for k, v in names.items()}, open(os.path.join(TAB, "macro_index.json"), "w"), indent=0)
    for f in (table_cases, table_remedies, table_examples, table_cost, table_toolval, table_noise, table_planted):
        f()
    table_wave(1)
    table_wave(2)
    table_h1()
    table_selection()
    print(f"{len(out)} macros, tables written to {TAB}")


if __name__ == "__main__":
    main()
