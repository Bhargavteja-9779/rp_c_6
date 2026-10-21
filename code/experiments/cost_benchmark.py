"""Experiment G: computational cost of the label-free audit and of novelty-Mondrian vs split CP.
Times (median of 5 repetitions, single core) on the five largest datasets of each suite."""
import json, os, sys, time
import numpy as np, pandas as pd
os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.data import load_dataset, row_keys
from dupcp.audit import audit
from dupcp.splits import random_split
from dupcp.conformal import conformal_quantile, thresholds, test_thresholds
from dupcp.models import fit_predict
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
aud = pd.read_csv(os.path.join(ROOT, "results", "tables", "T1_audit.csv"))
sel = aud.sort_values("n_rows", ascending=False).groupby("task").head(5)
def med_time(f, reps=5):
    ts = []
    for _ in range(reps):
        t = time.perf_counter(); f(); ts.append(time.perf_counter() - t)
    return float(np.median(ts))
rows = []
for _, r in sel.iterrows():
    d = load_dataset(int(r.data_id), r.task, os.path.join(ROOT, "data_cache"))
    X, y = d["X"], d["y"]
    t_key = med_time(lambda: row_keys(X))
    keys = row_keys(X)
    t_aud = med_time(lambda: audit(keys, y, r.task))
    tr, ca, te = random_split(len(y), 0)
    t_tax = med_time(lambda: (lambda s: (np.isin(keys[ca], keys[tr]), np.isin(keys[te], keys[tr])))(None))
    seen_ca = np.isin(keys[ca], keys[tr]).astype(int); seen_te = np.isin(keys[te], keys[tr]).astype(int)
    rng = np.random.default_rng(0); sc = rng.random(len(ca))
    t_scp = med_time(lambda: conformal_quantile(sc, 0.1), 50)
    t_mcp = med_time(lambda: test_thresholds(thresholds(sc, seen_ca, 0.1), seen_te, len(te)), 50)
    t0 = time.perf_counter()
    fit_predict("lgbm", r.task, X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], 0, n_classes=int(y.max()) + 1 if r.task == "classification" else None)
    t_fit = time.perf_counter() - t0
    rows.append(dict(task=r.task, data_id=int(r.data_id), name=r["name"], n_rows=len(y), n_features=X.shape[1],
                     t_keys_s=t_key, t_audit_s=t_aud, t_taxonomy_s=t_tax, t_scp_threshold_s=t_scp,
                     t_mcp_threshold_s=t_mcp, t_lgbm_fit_predict_s=t_fit))
    print(rows[-1], flush=True)
df = pd.DataFrame(rows)
os.makedirs(os.path.join(ROOT, "results", "verification"), exist_ok=True)
df.to_csv(os.path.join(ROOT, "results", "tables", "T9_cost.csv"), index=False)
