"""E10 (post hoc, D15c): planted-leak test of the duplicate audit.

Rule (fixed before running): the first five duplicate-free benchmark data sets with >= 1,000 rows,
in OpenML-id order. For each, one random 60/20/20 split (seed 0). We copy a known share f of the test
rows into the training part (exact copies, with their labels), so that exactly those test rows are
leaked. The audit must flag exactly the planted rows. The same is repeated with copies jittered by
0.1% of each numeric feature's SD, which the exact audit is known not to see. The clean split is the
negative control (no row may be flagged).
"""
import json, os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.data import load_dataset, row_keys
from dupcp.splits import random_split

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "results", "e10_planted_leak")
IDS = [(3, "classification"), (28, "classification"), (31, "classification"), (32, "classification"),
       (151, "classification")]


def audit_seen(X_tr, X_te):
    tr = set(row_keys(X_tr).tolist())
    return np.array([k in tr for k in row_keys(X_te)])


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for did, task in IDS:
        d = load_dataset(did, task, os.path.join(ROOT, "data_cache"))
        X = d["X"]
        tr, ca, te = random_split(len(X), 0)
        X_tr, X_te = X.iloc[tr].reset_index(drop=True), X.iloc[te].reset_index(drop=True)
        base = audit_seen(X_tr, X_te)
        rows.append(dict(data_id=did, name=d["name"], plant="none", f=0.0, planted=0, flagged=int(base.sum()),
                         true_pos=0, false_pos=int(base.sum())))
        num = X.select_dtypes("number").columns
        for f in (0.05, 0.20):
            rng = np.random.default_rng(1)
            idx = rng.choice(len(X_te), int(round(f * len(X_te))), replace=False)
            truth = np.zeros(len(X_te), bool)
            truth[idx] = True
            for kind in ("exact", "jitter_0.001sd"):
                C = X_te.iloc[idx].copy()
                if kind != "exact":
                    sd = X[num].std().replace(0, 1.0)
                    C[num] = C[num] + 0.001 * sd.values * rng.standard_normal((len(C), len(num)))
                flagged = audit_seen(pd.concat([X_tr, C], ignore_index=True), X_te)
                rows.append(dict(data_id=did, name=d["name"], plant=kind, f=f, planted=int(truth.sum()),
                                 flagged=int(flagged.sum()), true_pos=int((flagged & truth).sum()),
                                 false_pos=int((flagged & ~truth).sum())))
    df = pd.DataFrame(rows)
    df["recall"] = np.where(df.planted > 0, df.true_pos / df.planted.clip(lower=1), np.nan)
    summary = dict(
        n_datasets=len(IDS),
        clean_false_pos=int(df[df.plant == "none"].false_pos.sum()),
        exact_recall_min=float(df[df.plant == "exact"].recall.min()),
        exact_false_pos=int(df[df.plant == "exact"].false_pos.sum()),
        jitter_recall_max=float(df[df.plant.str.startswith("jitter") & (df.name != "kr-vs-kp")].recall.max()),
        jitter_note="kr-vs-kp has no numeric features, so its jittered copies are exact copies",
        planted_total=int(df[df.plant == "exact"].planted.sum()))
    json.dump(dict(summary=summary, rows=df.to_dict("records")), open(os.path.join(OUT, "planted_leak.json"), "w"),
              indent=1, default=float)
    print(df.to_string()); print(summary)


if __name__ == "__main__":
    main()
