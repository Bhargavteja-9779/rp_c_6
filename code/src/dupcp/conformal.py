"""Split and Mondrian conformal prediction for classification and regression."""
from __future__ import annotations

import numpy as np


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    """ceil((n+1)(1-alpha))-th smallest score; +inf if that rank exceeds n (Vovk et al.)."""
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    if k > n or n == 0:
        return np.inf
    return float(np.partition(scores, k - 1)[k - 1])


# ---------------------------------------------------------------- classification scores
def lac_scores(P: np.ndarray) -> np.ndarray:
    """Score matrix s(x, y) = 1 - p_y (Sadinle et al. 2019)."""
    return 1.0 - P


def aps_scores(P: np.ndarray, U: np.ndarray | None = None) -> np.ndarray:
    """APS score (Romano et al. 2020): probability mass of labels ranked above y plus U * p_y.

    With U ~ Uniform(0,1) per example this is the randomized APS of the original paper; U=None
    gives the deterministic variant (mass ranked at or above y), which is very conservative for
    binary problems.
    """
    order = np.argsort(-P, axis=1, kind="stable")
    sorted_p = np.take_along_axis(P, order, axis=1)
    cum = np.cumsum(sorted_p, axis=1)
    S = np.empty_like(P)
    np.put_along_axis(S, order, cum, axis=1)
    if U is not None:
        S = S - (1.0 - U)[:, None] * P
    return S


CLS_SCORES = {"lac": lac_scores, "aps": aps_scores}


# ---------------------------------------------------------------- generic machinery
def thresholds(cal_scores: np.ndarray, cal_groups: np.ndarray | None, alpha: float,
               groups=(0, 1)) -> dict:
    """Per-group conformal thresholds; cal_groups=None gives the single marginal threshold."""
    if cal_groups is None:
        return {"all": conformal_quantile(cal_scores, alpha)}
    return {g: conformal_quantile(cal_scores[cal_groups == g], alpha) for g in groups}


def test_thresholds(thr: dict, test_groups: np.ndarray | None, n_test: int) -> np.ndarray:
    if test_groups is None:
        return np.full(n_test, thr["all"])
    out = np.empty(n_test)
    for g, q in thr.items():
        out[test_groups == g] = q
    return out


def classification_sets(S_test: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Boolean membership matrix of prediction sets {y : s(x, y) <= q(x)}."""
    return S_test <= q[:, None]


def regression_intervals(lo: np.ndarray, hi: np.ndarray, q: np.ndarray):
    return lo - q, hi + q


def pac_quantile(scores: np.ndarray, alpha: float, delta: float) -> float:
    """Training-conditional (PAC) split-conformal threshold (Vovk 2012).

    With continuous scores, the coverage of the r-th smallest calibration score is Beta(r, n - r + 1).
    Return the smallest-rank score r with P{Beta(r, n - r + 1) < 1 - alpha} <= delta; +inf if none.
    """
    from scipy.stats import beta
    n = len(scores)
    if n == 0:
        return np.inf
    r = np.arange(1, n + 1)
    ok = beta.cdf(1 - alpha, r, n - r + 1) <= delta
    if not ok.any():
        return np.inf
    k = int(r[ok][0])
    return float(np.partition(scores, k - 1)[k - 1])


def pac_thresholds(cal_scores, cal_groups, alpha, delta, groups=(0, 1)) -> dict:
    return {g: pac_quantile(cal_scores[cal_groups == g], alpha, delta) for g in groups}
