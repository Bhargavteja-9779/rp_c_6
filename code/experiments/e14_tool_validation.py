"""E14 (post hoc, D15e): validate the covercheck *tool* on plain CSV files, outside the research pipeline.

Rule (fixed before running): every wave-2 data set with at most 30,000 rows (so that the tool sees the
same rows as the pipeline, without subsampling). Each is downloaded afresh from the UCI repository into
a plain folder (data_raw/, not the pipeline cache) and written as CSV. The installed `covercheck`
command is then run on the file with its defaults (random forest, 10 splits, seed 0), exactly as a user
would.

Compared with the pipeline:
  * check: the tool's expected exposure must equal the pipeline's label-free prediction (same formula,
    same rows);
  * verdict: the tool's flag must match the paper's combined rule;
  * coverage: the tool's new-case coverage (standard and fixed) must agree with the pipeline's random
    forest within sampling noise. The preprocessing, seeds and number of splits differ: 10 tool splits
    versus 20 pipeline splits.
"""
import contextlib, io, json, os, re, subprocess, sys
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "data_raw")
OUT = os.path.join(ROOT, "results", "e14_tool_validation")


def fetch_plain(uid):
    """Download from UCI (not from the pipeline cache) and write a plain CSV with a 'target' column."""
    from ucimlrepo import fetch_ucirepo
    path = os.path.join(RAW, f"uci{uid}.csv")
    if not os.path.exists(path):
        with contextlib.redirect_stdout(io.StringIO()):
            ds = fetch_ucirepo(id=uid)
        X, Y = ds.data.features.copy(), ds.data.targets
        cols, seen = [], {}
        for c in map(str, X.columns):
            seen[c] = seen.get(c, 0) + 1
            cols.append(c if seen[c] == 1 else f"{c}__{seen[c]}")
        X.columns = cols
        X["target"] = Y.iloc[:, 0].values
        X.to_csv(path, index=False)
    return path


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    sel = json.load(open(os.path.join(ROOT, "results", "reinforcement", "prospective_selection_w2.json")))
    sc = pd.read_csv(os.path.join(ROOT, "results", "reinforcement", "tables", "screening.csv"))
    P = pd.concat([pd.read_csv(os.path.join(ROOT, "results", "reinforcement", "prospective_w2", f))
                   for f in os.listdir(os.path.join(ROOT, "results", "reinforcement", "prospective_w2"))])
    P = P[(P.model == "rf") & P.score.isin(["lac", "absres"])]
    rows = []
    for x in sel["included"]:
        if x["n_raw"] > 30_000:
            continue
        uid = x["uci_id"]
        path = fetch_plain(uid)
        js = os.path.join(OUT, f"uci{uid}.json")
        if not os.path.exists(js):
            subprocess.run(["covercheck", path, "--target", "target", "--task", x["task"], "--splits", "10",
                            "--json", js], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t = json.load(open(js))
        summ = {r["mode"]: r for r in t["summary"]}
        pp = P[P.data_id == x["data_id"]]
        s_row = sc[sc.data_id == x["data_id"]].iloc[0]
        rows.append(dict(data_id=x["data_id"], name=x["name"], task=x["task"], rows=x["n_raw"],
                         exposure_pipeline=x["pred_exposure"], exposure_tool=t["check"]["exposure"],
                         flag_pipeline=bool(s_row.flag), verdict_tool=t["check"]["verdict"].split(":")[0],
                         new_std_tool=summ["standard"]["coverage_new"], new_fix_tool=summ["exact"]["coverage_new"],
                         new_std_pipeline=pp[pp.method == "SCP"].cov_novel.mean(),
                         new_fix_pipeline=pp[pp.method == "MCP"].cov_novel.mean(),
                         sd_std_pipeline=pp[pp.method == "SCP"].cov_novel.std(),
                         sd_fix_pipeline=pp[pp.method == "MCP"].cov_novel.std()))
        print(rows[-1]["name"], rows[-1]["verdict_tool"], round(rows[-1]["exposure_tool"], 4),
              round(rows[-1]["exposure_pipeline"], 4), flush=True)
    df = pd.DataFrame(rows)
    df["flag_tool"] = df.verdict_tool.str.startswith("FIX")
    df["exposure_absdiff"] = (df.exposure_tool - df.exposure_pipeline).abs()
    # difference of means from 10 vs 20 splits: standard error from the per-split SDs
    for k in ("std", "fix"):
        df[f"diff_{k}"] = df[f"new_{k}_tool"] - df[f"new_{k}_pipeline"]
        se = df[f"sd_{k}_pipeline"] * np.sqrt(1 / 10 + 1 / 20)
        df[f"within_2se_{k}"] = df[f"diff_{k}"].abs() <= 2 * se.fillna(0) + 1e-9
    summary = dict(n=len(df), exposure_max_absdiff=float(df.exposure_absdiff.max()),
                   flag_agreement=int((df.flag_tool == df.flag_pipeline).sum()),
                   within_2se_std=int(df.within_2se_std.sum()), within_2se_fix=int(df.within_2se_fix.sum()),
                   median_absdiff_std=float(df.diff_std.abs().median()), median_absdiff_fix=float(df.diff_fix.abs().median()),
                   max_absdiff_fix=float(df.diff_fix.abs().max()), min_new_fix_tool=float(df.new_fix_tool.min()))
    json.dump(dict(summary=summary, rows=df.to_dict("records")), open(os.path.join(OUT, "tool_validation.json"), "w"),
              indent=1, default=float)
    print(df[["name", "rows", "exposure_absdiff", "flag_tool", "flag_pipeline", "new_std_tool", "new_std_pipeline",
              "new_fix_tool", "new_fix_pipeline", "within_2se_fix"]].round(3).to_string())
    print(summary)


if __name__ == "__main__":
    main()
