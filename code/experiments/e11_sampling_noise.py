"""E11 (post hoc, D15a): is the split-to-split variation of new-case coverage just sampling noise?

Under exchangeability with continuous scores, the coverage of a conformal threshold at rank r among n
calibration scores is Beta(r, n - r + 1). The coverage *observed* on m test rows is then
Binomial(m, c) / m. For every fresh data set, learner, method and split we use the observed numbers
of new calibration rows n and new test rows m. We simulate the probability that observed new-case
coverage falls below 0.87 ("bad split") under pure noise, and compare it with the observed rate.
Separate calibration (MCP, PAC-MCP) should match pure noise. Standard calibration (SCP) can exceed it,
because its threshold is not calibrated on new rows.
"""
import glob, json, os, sys
import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
R = os.path.join(ROOT, "results", "reinforcement")
OUT = os.path.join(ROOT, "results", "e11_sampling_noise")
A, BAD, DELTA, SIMS = 0.1, 0.87, 0.1, 4000


def rank(n, method):
    if method == "PAC_MCP":
        rs = np.arange(1, n + 1)
        ok = np.flatnonzero(beta_dist.cdf(1 - A, rs, n - rs + 1) <= DELTA)
        return int(rs[ok[0]]) if len(ok) else n + 1
    return int(np.ceil((n + 1) * (1 - A)))


def p_bad(n, m, method, rng):
    if m == 0:
        return np.nan
    r = rank(n, method)
    if r > n:  # full set: coverage 1
        return 0.0
    c = rng.beta(r, n - r + 1, SIMS)
    return float(np.mean(rng.binomial(m, c) / m < BAD))


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(0)
    files = glob.glob(os.path.join(R, "prospective", "prosp_*.csv")) + glob.glob(os.path.join(R, "prospective_w2", "w2_*.csv"))
    P = pd.concat([pd.read_csv(f).assign(wave=2 if "/w2_" in f else 1) for f in files], ignore_index=True)
    if "error" in P:
        P = P[P.error.isna()]
    P = P[P.score.isin(["lac", "absres"]) & P.method.isin(["SCP", "MCP", "PAC_MCP"]) & (P.n_te_novel > 0)]
    # for SCP the noise model uses its own calibration size n (all rows) with the test-new count m
    P["n_cal"] = np.where(P.method == "SCP", P.n_ca_seen + P.n_ca_novel, P.n_ca_novel)
    P["expected_bad"] = [p_bad(int(n), int(m), meth, rng) for n, m, meth in zip(P.n_cal, P.n_te_novel, P.method)]
    P["observed_bad"] = (P.cov_novel < BAD).astype(float)
    summ = []
    for (meth, model), g in P.groupby(["method", "model"]):
        e, o = g.expected_bad.sum(), g.observed_bad.sum()
        # null distribution of the total count: sum of independent Bernoulli(expected_bad)
        tot = (rng.random((2000, len(g))) < g.expected_bad.values).sum(1)
        summ.append(dict(method=meth, model=model, n_splits=len(g), observed=int(o), expected=float(e),
                         ratio=float(o / e) if e else np.nan,
                         p_excess=float(np.mean(tot >= o)), p_deficit=float(np.mean(tot <= o))))
    S = pd.DataFrame(summ)
    by_ds = P.groupby(["wave", "name", "model", "method"])[["expected_bad", "observed_bad"]].mean().reset_index()
    json.dump(dict(summary=S.to_dict("records"), by_dataset=by_ds.round(4).to_dict("records")),
              open(os.path.join(OUT, "noise_check.json"), "w"), indent=1, default=float)
    print(S.round(3).to_string())


if __name__ == "__main__":
    main()
