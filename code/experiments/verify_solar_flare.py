"""Verification run (post hoc): is the MCP under-coverage on solar_flare (10 seeds) sampling noise?
Repeats SCP-R / MCP-R with 200 random splits for ridge and LightGBM (|residual| score, alpha=0.1)."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.data import load_dataset
from dupcp.models import fit_predict
from dupcp.splits import random_split
from dupcp.conformal import thresholds, test_thresholds, conformal_quantile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
d = load_dataset(44966, "regression", os.path.join(ROOT, "data_cache"))
X, y, keys = d["X"], d["y"], d["keys"]
rows = []
for seed in range(1000, 1200):
    tr, ca, te = random_split(len(y), seed)
    tk = set(keys[tr].tolist())
    sca = np.array([k in tk for k in keys[ca]], int); ste = np.array([k in tk for k in keys[te]], int)
    for model in ["logreg", "lgbm"]:
        yc, yt = fit_predict(model, "regression", X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed)
        sc, st = np.abs(y[ca] - yc), np.abs(y[te] - yt)
        qs = conformal_quantile(sc, 0.1)
        thr = thresholds(sc, sca, 0.1)
        qm = test_thresholds(thr, ste, len(te))
        nov = ste == 0
        rows.append(dict(seed=seed, model=model, n_nov_te=int(nov.sum()), n_nov_ca=int((sca == 0).sum()),
                         scp_novel=float((st[nov] <= qs).mean()), mcp_novel=float((st[nov] <= qm[nov]).mean()),
                         mcp_novel_hits=int((st[nov] <= qm[nov]).sum())))
df = pd.DataFrame(rows)
out = {}
for m, g in df.groupby("model"):
    pooled = g.mcp_novel_hits.sum() / g.n_nov_te.sum()
    b = [np.mean(np.random.default_rng(i).choice(g.mcp_novel, len(g))) for i in range(5000)]
    out[m] = dict(n_splits=len(g), scp_novel_mean=g.scp_novel.mean(), mcp_novel_mean=g.mcp_novel.mean(),
                  mcp_novel_pooled=pooled, mcp_mean_ci=[float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
                  mcp_per_split_sd=g.mcp_novel.std())
print(json.dumps(out, indent=1))
os.makedirs(os.path.join(ROOT, "results", "verification"), exist_ok=True)
df.to_csv(os.path.join(ROOT, "results", "verification", "solar_flare_200splits.csv"), index=False)
json.dump(out, open(os.path.join(ROOT, "results", "verification", "solar_flare_200splits.json"), "w"), indent=1)
