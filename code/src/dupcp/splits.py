"""Row-level (protocol R) and record-group-level (protocol G) train/calibration/test splits."""
from __future__ import annotations

import numpy as np


def random_split(n: int, seed: int, fracs=(0.6, 0.2, 0.2)):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    a = int(round(fracs[0] * n))
    b = a + int(round(fracs[1] * n))
    return perm[:a], perm[a:b], perm[b:]


def group_split(keys: np.ndarray, seed: int, fracs=(0.6, 0.2, 0.2)):
    """Assign whole record groups to one partition; group order is random.

    Groups are added to train until it holds >= fracs[0] of the rows, then to calibration until
    the cumulative share reaches fracs[0] + fracs[1]; the rest form the test set.
    """
    rng = np.random.default_rng(seed + 10_000)
    uniq, inv = np.unique(keys, return_inverse=True)
    sizes = np.bincount(inv)
    order = rng.permutation(len(uniq))
    cum = np.cumsum(sizes[order]) / len(keys)
    part = np.full(len(uniq), 2)
    part[order[cum <= fracs[0] + 1e-12]] = 0
    in_cal = (cum > fracs[0] + 1e-12) & (cum <= fracs[0] + fracs[1] + 1e-12)
    part[order[in_cal]] = 1
    row_part = part[inv]
    idx = np.arange(len(keys))
    return idx[row_part == 0], idx[row_part == 1], idx[row_part == 2]
