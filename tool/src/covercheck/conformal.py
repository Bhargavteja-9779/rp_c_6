"""Step 2, *fix*: split conformal prediction calibrated separately for seen and new cases."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist

from .check import row_keys


def _rank_threshold(scores: np.ndarray, alpha: float, delta: float | None) -> float:
    """Conformal threshold: the ceil((n+1)(1-alpha))-th smallest score. With delta, the smallest rank
    r with P(Beta(r, n-r+1) < 1-alpha) <= delta (coverage >= 1-alpha with probability >= 1-delta over
    the calibration draw). Returns +inf when no finite threshold is valid (honest full set)."""
    s = np.sort(np.asarray(scores, dtype=float))
    n = len(s)
    if n == 0:
        return np.inf
    if delta is None:
        r = int(np.ceil((n + 1) * (1 - alpha)))
    else:
        rs = np.arange(1, n + 1)
        ok = np.flatnonzero(beta_dist.cdf(1 - alpha, rs, n - rs + 1) <= delta)
        r = int(rs[ok[0]]) if len(ok) else n + 1
    return float(s[r - 1]) if r <= n else np.inf


class SeenNewConformal:
    """Wrap a scikit-learn estimator and calibrate seen and new cases separately.

    A case is *seen* if its feature vector occurs exactly in the training data. With
    ``mode="distance"``, cases are instead grouped by their distance to the nearest training rows
    (exact copies form one group, the rest form five distance bands), which also handles near-copies.

    Coverage of at least 1 - alpha holds separately for every group, so it holds for any mix of seen
    and new cases at deployment (Mondrian conformal prediction).
    """

    def __init__(self, estimator, task: str = "classification", alpha: float = 0.1, mode: str = "exact",
                 delta: float | None = None, n_neighbors: int = 10):
        if task not in ("classification", "regression"):
            raise ValueError("task must be 'classification' or 'regression'")
        if mode not in ("exact", "distance", "standard"):
            raise ValueError("mode must be 'exact', 'distance' or 'standard'")
        self.estimator, self.task, self.alpha, self.mode = estimator, task, alpha, mode
        self.delta, self.n_neighbors = delta, n_neighbors

    # ---------------------------------------------------------------- fitting
    def fit(self, X, y):
        X = pd.DataFrame(X)
        self.estimator.fit(X, y)
        self._train_keys = set(row_keys(X).tolist())
        if self.mode == "distance":
            self.fit_distance_index(X)
        return self

    def fit_distance_index(self, X_train):
        """Nearest-neighbour index on standardized numeric training features (distance mode)."""
        from sklearn.neighbors import NearestNeighbors
        X_train = pd.DataFrame(X_train)
        self._num = X_train.select_dtypes("number").columns
        Z = X_train[self._num].to_numpy(dtype=float)
        self._mu, self._sd = np.nanmean(Z, 0), np.nanstd(Z, 0) + 1e-12
        self._nn = NearestNeighbors(n_neighbors=1).fit(np.nan_to_num((Z - self._mu) / self._sd))
        return self

    def _scores_all(self, X):
        """Nonconformity score for every candidate label (classification) or the prediction (regression)."""
        if self.task == "classification":
            P = self.estimator.predict_proba(X)
            return 1 - P
        return self.estimator.predict(X)

    def _seen_dist(self, X):
        X = pd.DataFrame(X)
        seen = np.array([k in self._train_keys for k in row_keys(X)], dtype=int)
        if self.mode != "distance":
            return seen, None
        Z = np.nan_to_num((X[self._num].to_numpy(dtype=float) - self._mu) / self._sd)
        return seen, self._nn.kneighbors(Z)[0][:, 0]

    def groups(self, X) -> np.ndarray:
        """0 = new, 1 = seen (exact mode); 0 = exact copy, 1..5 = distance bands (distance mode)."""
        seen, dist = self._seen_dist(X)
        if self.mode == "standard":
            return np.zeros(len(seen), dtype=int)
        if self.mode == "exact":
            return seen
        return np.where(seen == 1, 0, 1 + np.searchsorted(self._edges, dist, side="right"))

    def is_seen(self, X) -> np.ndarray:
        return np.array([k in self._train_keys for k in row_keys(pd.DataFrame(X))], dtype=bool)

    def calibrate(self, X_cal, y_cal):
        """Compute one threshold per group from held-out calibration data (not used for fitting)."""
        X_cal = pd.DataFrame(X_cal)
        y_cal = np.asarray(y_cal)
        if self.task == "classification":
            self.classes_ = np.asarray(self.estimator.classes_)
            idx = np.searchsorted(self.classes_, y_cal)
            s = self._scores_all(X_cal)[np.arange(len(y_cal)), idx]
        else:
            s = np.abs(y_cal - self._scores_all(X_cal))
        if self.mode == "distance":
            seen, dist = self._seen_dist(X_cal)
            new_d = dist[seen == 0]
            self._edges = np.quantile(new_d, [0.2, 0.4, 0.6, 0.8]) if len(new_d) else np.zeros(4)
            g = self.groups(X_cal)
            labels = range(6)
        else:
            g = self.groups(X_cal)
            labels = (0, 1) if self.mode == "exact" else (0,)
        self.thresholds_ = {k: _rank_threshold(s[g == k], self.alpha, self.delta) for k in labels}
        self.n_cal_ = {k: int((g == k).sum()) for k in labels}
        return self

    # ---------------------------------------------------------------- prediction
    def _q(self, X):
        g = self.groups(X)
        return np.array([self.thresholds_[k] for k in g]), g

    def predict_set(self, X) -> np.ndarray:
        """Boolean matrix (n_samples, n_classes): label j is in the set of case i."""
        q, _ = self._q(X)
        return self._scores_all(X) <= q[:, None]

    def predict_interval(self, X) -> np.ndarray:
        """Array (n_samples, 2) of lower and upper interval ends."""
        q, _ = self._q(X)
        yhat = self._scores_all(X)
        return np.column_stack([yhat - q, yhat + q])

    def covered(self, X, y) -> np.ndarray:
        y = np.asarray(y)
        if self.task == "classification":
            S = self.predict_set(X)
            return S[np.arange(len(y)), np.searchsorted(self.classes_, y)]
        iv = self.predict_interval(X)
        return (iv[:, 0] <= y) & (y <= iv[:, 1])
