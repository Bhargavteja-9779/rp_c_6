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


def purity_exposure(keys: np.ndarray, y: np.ndarray, tr: np.ndarray, te: np.ndarray, task: str) -> tuple[float, float]:
    """Exposure pi and label-purity-adjusted exposure pi_P on one realised split (Proposition 4).

    A test row counts towards pi_P if it has at least one training row with the same feature key and
    every such training row carries exactly the test row's label (classification) or target value
    (regression). Uses labels and group structure only; no model.
    """
    import pandas as pd
    yy = y if task == "classification" else np.round(np.asarray(y, float), 12)
    trd = pd.DataFrame({"k": keys[tr], "y": yy[tr]})
    stats = trd.groupby("k")["y"].agg(["nunique", "first"])
    ted = pd.DataFrame({"k": keys[te], "y": yy[te]})
    m = ted.join(stats, on="k")
    seen = m["nunique"].notna().to_numpy()
    pure = seen & (m["nunique"].to_numpy() == 1) & (m["first"].to_numpy() == m["y"].to_numpy())
    return float(seen.mean()), float(pure.mean())


def purity_bound(pi_p: float, alpha: float) -> float:
    """Predicted novel-record coverage gap under Proposition 4: -alpha*pi_P/(1-pi_P), floored at -(1-alpha)."""
    if pi_p >= 1 - alpha:
        return -(1 - alpha)
    return -alpha * pi_p / (1 - pi_p)
