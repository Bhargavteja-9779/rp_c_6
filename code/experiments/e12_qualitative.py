"""E12 (post hoc, D15b): qualitative examples chosen by a fixed rule, never by hand.

Data: NASA mc1 (OpenML 1056), random forest, the first random split (seed 0), LAC score, alpha = 0.1.
The rule was fixed before looking at any example:
  (a) the first seen test module in data-set row order;
  (b) the first four new test modules in data-set row order, whatever their outcome;
  (c) the first new test module that is truly defective;
  (d) the first new test module where the *fixed* set misses the true label (a failure case).
For each we show four metrics, the true label and the prediction sets of standard calibration and of
separate calibration.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.conformal import classification_sets, test_thresholds, thresholds
from dupcp.data import load_dataset
from dupcp.models import fit_predict
from dupcp.splits import random_split

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "results", "e12_qualitative")
SHOW = ["LOC_TOTAL", "CYCLOMATIC_COMPLEXITY", "NUM_OPERATORS", "HALSTEAD_EFFORT"]
NAMES = {0: "no defect", 1: "defect"}


def main():
    os.makedirs(OUT, exist_ok=True)
    d = load_dataset(1056, "classification", os.path.join(ROOT, "data_cache"))
    X, y, keys = d["X"], d["y"], d["keys"]
    tr, ca, te = random_split(len(y), 0)
    tr_keys = set(keys[tr].tolist())
    seen_ca = np.array([k in tr_keys for k in keys[ca]], dtype=int)
    seen_te = np.array([k in tr_keys for k in keys[te]], dtype=int)
    Pc, Pt = fit_predict("rf", "classification", X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], 0, n_classes=2)
    sc = 1 - Pc[np.arange(len(ca)), y[ca]]
    q_std = test_thresholds(thresholds(sc, None, 0.1, (0, 1)), None, len(te))
    q_fix = test_thresholds(thresholds(sc, seen_ca, 0.1, (0, 1)), seen_te, len(te))
    S_std, S_fix = classification_sets(1 - Pt, q_std), classification_sets(1 - Pt, q_fix)
    order = np.argsort(te)  # data-set row order
    pick = []
    seen_idx = [i for i in order if seen_te[i] == 1][:1]
    new_idx = [i for i in order if seen_te[i] == 0]
    pick += [(i, "first seen module") for i in seen_idx]
    pick += [(i, "first new modules (any outcome)") for i in new_idx[:4]]
    pick += [(i, "first new defective module") for i in new_idx if y[te][i] == 1][:1]
    pick += [(i, "first new module the fixed set misses") for i in new_idx if not S_fix[i, y[te][i]]][:1]
    lab = lambda row: "{" + ", ".join(NAMES[j] for j in (0, 1) if row[j]) + "}" if row.any() else "{ } (empty)"
    rows = []
    for i, why in pick:
        r = dict(rule=why, row=int(te[i]), seen=bool(seen_te[i]), true=NAMES[int(y[te][i])],
                 p_defect=float(Pt[i, 1]), set_standard=lab(S_std[i]), set_fixed=lab(S_fix[i]),
                 covered_standard=bool(S_std[i, y[te][i]]), covered_fixed=bool(S_fix[i, y[te][i]]))
        r.update({k: float(X.iloc[te[i]][k]) for k in SHOW})
        rows.append(r)
    out = dict(dataset="mc1", model="rf", seed=0, thresholds=dict(standard=float(q_std[0]),
               fixed_new=float(q_fix[seen_te == 0][0]), fixed_seen=float(q_fix[seen_te == 1][0])), rows=rows)
    json.dump(out, open(os.path.join(OUT, "examples.json"), "w"), indent=1)
    for r in rows:
        print(r)
    print(out["thresholds"])


def class_conditional(seeds=range(10)):
    """Post hoc failure analysis: coverage of new *defective* modules on mc1 (RF, LAC, alpha = 0.1) for
    standard calibration, the fix (seen/new), and the fix refined by class (seen/new x label; label-
    conditional Mondrian CP, Vovk et al. 2022). Sets include label j if score_j <= q[group, j]."""
    d = load_dataset(1056, "classification", os.path.join(ROOT, "data_cache"))
    X, y, keys = d["X"], d["y"], d["keys"]
    rows = []
    for seed in seeds:
        tr, ca, te = random_split(len(y), seed)
        tk = set(keys[tr].tolist())
        sca = np.array([k in tk for k in keys[ca]], dtype=int)
        ste = np.array([k in tk for k in keys[te]], dtype=int)
        Pc, Pt = fit_predict("rf", "classification", X.iloc[tr], y[tr], [X.iloc[ca], X.iloc[te]], seed, n_classes=2)
        sc = 1 - Pc[np.arange(len(ca)), y[ca]]
        S = 1 - Pt
        q_std = thresholds(sc, None, 0.1, (0, 1))["all"]
        qf = thresholds(sc, sca, 0.1, (0, 1))
        sets = {"standard": S <= q_std,
                "fix (seen/new)": S <= np.array([qf[g] for g in ste])[:, None]}
        cc = np.zeros_like(S, dtype=bool)
        for g in (0, 1):
            for j in (0, 1):
                m = (sca == g) & (y[ca] == j)
                q = thresholds(sc[m], None, 0.1, (0, 1))["all"] if m.any() else np.inf
                cc[ste == g, j] = S[ste == g, j] <= q
        sets["fix by class (seen/new x label)"] = cc
        yt = y[te]
        for name, St in sets.items():
            cov = St[np.arange(len(te)), yt]
            for lab, lname in ((1, "defect"), (0, "no defect")):
                m = (ste == 0) & (yt == lab)
                rows.append(dict(seed=seed, method=name, label=lname, n=int(m.sum()),
                                 coverage=float(cov[m].mean()) if m.any() else np.nan,
                                 size=float(St[m].sum(1).mean()) if m.any() else np.nan))
    import pandas as pd
    df = pd.DataFrame(rows)
    agg = df.groupby(["method", "label"]).apply(lambda g: pd.Series(dict(
        n_total=int(g.n.sum()), coverage=float(np.nansum(g.coverage * g.n) / g.n.sum()),
        size=float(np.nansum(g["size"] * g.n) / g.n.sum())))).reset_index()
    json.dump(agg.to_dict("records"), open(os.path.join(OUT, "class_conditional.json"), "w"), indent=1)
    print(agg.round(3).to_string())


if __name__ == "__main__":
    main()
    class_conditional()
