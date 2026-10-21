import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dupcp.audit import audit, expected_exposure  # noqa: E402
from dupcp.conformal import aps_scores, conformal_quantile, lac_scores, thresholds  # noqa: E402
from dupcp.conformal import test_thresholds as per_test_thresholds  # noqa: E402
from dupcp.data import group_preserving_subsample, row_keys  # noqa: E402
from dupcp.metrics import ece_toplabel  # noqa: E402
from dupcp.splits import group_split, random_split  # noqa: E402


def test_quantile_rank_and_fallback():
    s = np.arange(1, 10, dtype=float)  # n=9, alpha=0.1 -> k=ceil(10*0.9)=9
    assert conformal_quantile(s, 0.1) == 9.0
    assert np.isinf(conformal_quantile(s[:8], 0.1))  # k=9 > n=8
    assert np.isinf(conformal_quantile(np.array([]), 0.1))


def test_split_cp_marginal_validity_exchangeable():
    rng = np.random.default_rng(0)
    covs = []
    for _ in range(3000):
        s = rng.random(51)
        q = conformal_quantile(s[:50], 0.1)
        covs.append(s[50] <= q)
    m = np.mean(covs)
    # theory: coverage in [0.9, 0.9 + 1/51]
    assert 0.885 < m < 0.93


def test_mondrian_group_validity_and_marginal_failure():
    """Seen points have tiny scores; marginal CP under-covers novel points, Mondrian does not."""
    rng = np.random.default_rng(1)
    cov_scp, cov_mcp = [], []
    for _ in range(2000):
        g = (rng.random(201) < 0.5).astype(int)          # 1 = seen
        s = np.where(g == 1, rng.random(201) * 0.01, rng.random(201))
        sc, gc, st, gt = s[:200], g[:200], s[200], g[200]
        if gt == 1:
            continue
        cov_scp.append(st <= conformal_quantile(sc, 0.1))
        thr = thresholds(sc, gc, 0.1)
        cov_mcp.append(st <= per_test_thresholds(thr, np.array([gt]), 1)[0])
    assert np.mean(cov_scp) < 0.85          # theory: about 1 - 0.1/(1-0.5) = 0.8
    assert abs(np.mean(cov_mcp) - 0.9) < 0.025


def test_lac_aps_scores():
    P = np.array([[0.7, 0.2, 0.1], [0.1, 0.3, 0.6]])
    assert np.allclose(lac_scores(P), 1 - P)
    A = aps_scores(P)
    assert np.allclose(A[0], [0.7, 0.9, 1.0])
    assert np.allclose(A[1], [1.0, 0.9, 0.6])


def test_row_keys_nan_and_categorical():
    X = pd.DataFrame({"a": [1.0, 1.0, np.nan, np.nan, 2.0], "b": pd.Categorical(["x", "x", "y", "y", "x"])})
    k = row_keys(X)
    assert k[0] == k[1] and k[2] == k[3] and k[0] != k[4] and k[0] != k[2]


def test_expected_exposure_matches_simulation():
    rng = np.random.default_rng(3)
    keys = np.concatenate([np.arange(300), np.repeat(np.arange(300, 350), 4), np.repeat(np.arange(350, 360), 10)])
    N = len(keys)
    n_tr = int(round(0.6 * N))
    pred = expected_exposure(keys, n_tr)
    sims = []
    for s in range(400):
        tr, ca, te = random_split(N, s)
        sims.append(np.isin(keys[te], keys[tr]).mean())
    assert abs(np.mean(sims) - pred) < 0.01


def test_group_split_disjoint_groups():
    keys = np.repeat(np.arange(100), np.arange(1, 101) % 4 + 1)
    tr, ca, te = group_split(keys, 0)
    assert len(set(keys[tr]) & set(keys[te])) == 0
    assert len(set(keys[tr]) & set(keys[ca])) == 0
    assert len(tr) + len(ca) + len(te) == len(keys)


def test_subsample_keeps_whole_groups():
    keys = np.repeat(np.arange(1000), 3)
    idx = group_preserving_subsample(keys, 900, 0)
    _, c = np.unique(keys[idx], return_counts=True)
    assert len(idx) == 900 and (c == 3).all()


def test_audit_conflicts():
    keys = np.array([1, 1, 2, 2, 3])
    y = np.array([0, 1, 0, 0, 1])
    a = audit(keys, y, "classification")
    assert a["dup_row_frac"] == pytest.approx(0.8)
    assert a["conflict_row_frac"] == pytest.approx(0.4)
    assert a["conflict_group_frac"] == pytest.approx(0.5)


def test_ece_perfect_and_bad():
    conf = np.full(1000, 0.8)
    correct = (np.arange(1000) % 5 != 0).astype(float)
    assert ece_toplabel(conf, correct) == pytest.approx(0.0)
    assert ece_toplabel(np.full(10, 0.9), np.zeros(10)) == pytest.approx(0.9)


def test_randomized_aps_exact_coverage():
    rng = np.random.default_rng(5)
    covs = []
    for _ in range(400):
        P = rng.dirichlet(np.ones(2), size=301)
        y = (rng.random(301) < P[:, 1]).astype(int)  # labels drawn from P: exchangeable
        S = aps_scores(P, rng.random(301))
        s = S[np.arange(301), y]
        covs.append(s[300] <= conformal_quantile(s[:300], 0.1))
    assert 0.86 < np.mean(covs) < 0.94


def test_pac_threshold_training_conditional():
    from dupcp.conformal import pac_quantile
    rng = np.random.default_rng(11)
    cov_plain, cov_pac = [], []
    for _ in range(3000):
        s = rng.random(40)  # calibration scores; test coverage of threshold t is exactly t (uniform)
        cov_plain.append(conformal_quantile(s, 0.1))
        cov_pac.append(min(pac_quantile(s, 0.1, 0.1), 1.0))
    # plain: about half of calibration draws give coverage below 0.9; PAC: at most delta = 10%
    assert np.mean(np.array(cov_plain) < 0.9) > 0.25
    assert np.mean(np.array(cov_pac) < 0.9) <= 0.12


def test_purity_exposure_and_bound():
    from dupcp.audit import purity_exposure, purity_bound
    keys = np.array([1, 1, 2, 2, 3, 3, 4])
    y = np.array([0, 0, 0, 1, 1, 1, 0])
    tr = np.array([0, 2, 4]); te = np.array([1, 3, 5, 6])
    pi, pi_p = purity_exposure(keys, y, tr, te, "classification")
    assert pi == pytest.approx(3 / 4)       # rows 1, 3, 5 have a training copy
    assert pi_p == pytest.approx(2 / 4)     # row 3 label differs from its training copy
    assert purity_bound(0.5, 0.1) == pytest.approx(-0.1)
    assert purity_bound(0.95, 0.1) == pytest.approx(-0.9)


def test_purity_limit_simulation():
    """Proposition 4: memorised pure rows score 0, all other rows share one score law."""
    rng = np.random.default_rng(3)
    covs = []
    pi_p = 0.4
    for _ in range(800):
        n = 2000
        pure = rng.random(n) < pi_p
        s = np.where(pure, 0.0, rng.random(n))
        q = conformal_quantile(s[:1000], 0.1)
        nov = ~pure[1000:]
        covs.append(np.mean(s[1000:][nov] <= q))
    assert abs(np.mean(covs) - (1 - 0.1 / (1 - pi_p))) < 0.01


def test_group_split_infeasible_raises():
    keys = np.concatenate([np.zeros(900, dtype=np.uint64), np.arange(1, 101, dtype=np.uint64)])
    with pytest.raises(ValueError):
        group_split(keys, 0)
