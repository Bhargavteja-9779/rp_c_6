"""Retrospective (non-blind) purity analysis: recompute pi and pi_P on the exact v1 splits
(seeds 0-9 main/external, 0-4 injection) and join with observed SCP-R novel gaps."""
import glob, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.audit import purity_exposure, purity_bound
from dupcp.data import load_dataset, row_keys
from dupcp.splits import random_split
from dupcp.experiments import inject_duplicates

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, "data_cache")
OUT = os.path.join(ROOT, "results", "reinforcement")
A = 0.1
rows = []
# --- suites + external
for src, pat in [("suite", "results/raw/audit_*.json"), ("external", "results/external/audit_*.json")]:
    for p in sorted(glob.glob(os.path.join(ROOT, pat))):
        a = json.load(open(p))
        if a["excess_row_frac"] == 0:
            continue
        d = load_dataset(a["data_id"], a["task"], CACHE)
        pis, pps = [], []
        for seed in range(10):
            tr, ca, te = random_split(len(d["y"]), seed)
            pi, pp = purity_exposure(d["keys"], d["y"], tr, te, a["task"])
            pis.append(pi); pps.append(pp)
        rows.append(dict(source=src, task=a["task"], data_id=a["data_id"], name=a["name"], pi=np.mean(pis),
                         pi_p=np.mean(pps), conflict_row_frac=a["conflict_row_frac"]))
pur = pd.DataFrame(rows)
# observed gaps (SCP-R, alpha 0.1, LAC / absres)
obs = []
for src, pat in [("suite", "results/raw/%s_*.csv"), ("external", "results/external/%s_*.csv")]:
    for task in ("classification", "regression"):
        for f in glob.glob(os.path.join(ROOT, pat % task)):
            d = pd.read_csv(f)
            if "error" in d:
                d = d[d.error.isna()]
            d = d[(d.protocol == "R") & np.isclose(d.alpha, A) & d.score.isin(["lac", "absres"])]
            g = d.groupby(["data_id", "model", "method"])["cov_novel"].mean().reset_index()
            g["source"] = src
            obs.append(g)
obs = pd.concat(obs)
obs = obs.pivot_table(index=["source", "data_id", "model"], columns="method", values="cov_novel").reset_index()
obs["gap_scp"] = obs["SCP"] - (1 - A)
obs["gap_mcp"] = obs["MCP"] - (1 - A)
retro = obs.merge(pur, on=["source", "data_id"])
retro["g_star"] = [purity_bound(p, A) for p in retro.pi_p]
retro["g_pi"] = [purity_bound(p, A) for p in retro.pi]
retro.to_csv(os.path.join(OUT, "purity_retrospective.csv"), index=False)

# --- injection experiment (exact copies with identical labels -> pi_P ~ pi)
inj_rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "results/inject/inject_*.csv"))):
    r = pd.read_csv(f)
    task, did = r.task.iloc[0], int(r.data_id.iloc[0])
    d = load_dataset(did, task, CACHE)
    X0, y0 = d["X"], d["y"]
    if len(y0) > 10000:
        idx = np.random.default_rng(did).choice(len(y0), 10000, replace=False)
        X0, y0 = X0.iloc[idx].reset_index(drop=True), y0[idx]
    for rate in sorted(r.rate.unique()):
        for seed in sorted(r.seed.unique()):
            X, y = inject_duplicates(X0, y0, rate, seed)
            keys = row_keys(X)
            tr, ca, te = random_split(len(y), seed)
            pi, pp = purity_exposure(keys, y, tr, te, task)
            inj_rows.append(dict(task=task, data_id=did, rate=rate, seed=seed, pi=pi, pi_p=pp))
ip = pd.DataFrame(inj_rows).groupby(["task", "data_id", "rate"])[["pi", "pi_p"]].mean().reset_index()
r = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(ROOT, "results/inject/inject_*.csv"))])
r = r[r.method == "SCP"].groupby(["task", "data_id", "rate", "model"])["cov_novel"].mean().reset_index()
r["gap_scp"] = r.cov_novel - (1 - A)
inj = r.merge(ip, on=["task", "data_id", "rate"])
inj["g_star"] = [purity_bound(p, A) for p in inj.pi_p]
inj.to_csv(os.path.join(OUT, "purity_injection.csv"), index=False)
print("retro rows", len(retro), "inj rows", len(inj))
