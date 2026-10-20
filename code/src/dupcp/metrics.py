"""Calibration metrics."""
from __future__ import annotations

import numpy as np


def ece_toplabel(conf: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float:
    """Top-label expected calibration error with equal-width bins (Naeini et al. 2015)."""
    if len(conf) == 0:
        return np.nan
    bins = np.minimum((conf * n_bins).astype(int), n_bins - 1)
    tot = 0.0
    for b in range(n_bins):
        m = bins == b
        if m.any():
            tot += m.sum() * abs(correct[m].mean() - conf[m].mean())
    return tot / len(conf)


def size_matched_ece(conf, correct, size, rng, draws=20, n_bins=15):
    """Mean ECE of random subsets of the given size; controls ECE's small-sample upward bias."""
    if size == 0 or size > len(conf):
        return np.nan
    vals = []
    for _ in range(draws):
        idx = rng.choice(len(conf), size=size, replace=False)
        vals.append(ece_toplabel(conf[idx], correct[idx], n_bins))
    return float(np.mean(vals))
