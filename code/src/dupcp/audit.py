"""Label-free duplicate audit and the exposure prediction of Proposition 2."""
from __future__ import annotations

import numpy as np
from scipy.special import gammaln


def group_sizes(keys: np.ndarray) -> np.ndarray:
    _, counts = np.unique(keys, return_counts=True)
    return counts


def expected_exposure(keys: np.ndarray, n_train: int) -> float:
    """Expected fraction of test rows with a feature-identical training row (Proposition 2).

    For a test row whose group has size m, P(novel) = C(N-m, n_T) / C(N-1, n_T).
    """
    m = group_sizes(keys)
    N = int(m.sum())

    def log_comb(a, b):
        return gammaln(a + 1) - gammaln(b + 1) - gammaln(a - b + 1)

    p_novel = np.where(N - m >= n_train,
                       np.exp(log_comb(N - m, n_train) - log_comb(N - 1, n_train)), 0.0)
    return float(np.sum(m / N * (1.0 - p_novel)))


def audit(keys: np.ndarray, y: np.ndarray, task: str, train_frac: float = 0.6) -> dict:
    m = group_sizes(keys)
    N = int(m.sum())
    in_dup = m[m > 1].sum()
    out = {
        "n_rows": N,
        "n_groups": int(len(m)),
        "dup_row_frac": float(in_dup / N),             # rows belonging to a group of size >= 2
        "excess_row_frac": float((N - len(m)) / N),    # rows that are redundant copies
        "max_group": int(m.max()),
        "pred_exposure": expected_exposure(keys, int(round(train_frac * N))),
    }
    # label conflicts: groups whose rows do not share a single label
    _, inv = np.unique(keys, return_inverse=True)
    if task == "classification":
        import pandas as pd
        nlab = pd.Series(y).groupby(inv).nunique().to_numpy()
    else:
        import pandas as pd
        nlab = pd.Series(np.round(y, 12)).groupby(inv).nunique().to_numpy()
    sizes = np.bincount(inv)
    out["conflict_group_frac"] = float(np.mean(nlab[sizes > 1] > 1)) if (sizes > 1).any() else 0.0
    out["conflict_row_frac"] = float(sizes[nlab > 1].sum() / N)
    return out
