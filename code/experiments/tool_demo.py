"""Run the covercheck tool on the NASA mc1 data exactly as a practitioner would (default random forest,
10 random splits) and store its outputs for the manuscript."""
import json, os, sys, time
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tool", "src"))
from covercheck import check, evaluate, summarize
from covercheck.cli import default_model

df = pd.read_csv(os.path.join(ROOT, "tool", "examples", "mc1.csv"))
y = df.pop("defective").astype(str).to_numpy()
t0 = time.time()
chk = check(df, y)
t_check = time.time() - t0
res = summarize(evaluate(default_model("classification", df), df, y, "classification", 0.1, n_splits=10))
out = os.path.join(ROOT, "results", "reinforcement", "tables")
res.to_csv(os.path.join(out, "tool_mc1.csv"))
json.dump(dict(chk.__dict__, seconds_check=t_check), open(os.path.join(out, "tool_mc1_check.json"), "w"), indent=1)
print(chk.summary()); print(res.round(3)); print("check seconds", round(t_check, 2))
