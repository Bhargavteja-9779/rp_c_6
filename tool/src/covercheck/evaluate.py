"""Step 3, *report*: measure coverage overall, on seen cases and on new cases, with and without the fix."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone

from .conformal import SeenNewConformal


def evaluate(estimator, X, y, task: str = "classification", alpha: float = 0.1, n_splits: int = 5,
             fracs=(0.6, 0.2, 0.2), modes=("standard", "exact"), delta: float | None = None,
             random_state: int = 0) -> pd.DataFrame:
    """Repeat random train/calibration/test splits and report coverage and set size for each mode.

    Returns one row per split and mode with columns coverage_all, coverage_seen, coverage_new,
    size_new, seen_share and empty_new (classification).
    """
    X = pd.DataFrame(X).reset_index(drop=True)
    y = np.asarray(y)
    rows = []
    for s in range(n_splits):
        rng = np.random.default_rng(random_state + s)
        perm = rng.permutation(len(y))
        a = int(round(fracs[0] * len(y)))
        b = a + int(round(fracs[1] * len(y)))
        tr, ca, te = perm[:a], perm[a:b], perm[b:]
        base = None
        for mode in modes:
            m = SeenNewConformal(clone(estimator), task, alpha, mode=mode, delta=delta)
            if base is None:
                m.fit(X.iloc[tr], y[tr])
                base = m
            else:  # reuse the fitted model: only the calibration differs between modes
                m.estimator, m._train_keys = base.estimator, base._train_keys
                if mode == "distance":
                    m.fit_distance_index(X.iloc[tr])
            m.calibrate(X.iloc[ca], y[ca])
            cov = m.covered(X.iloc[te], y[te])
            seen = m.is_seen(X.iloc[te])
            if task == "classification":
                size = m.predict_set(X.iloc[te]).sum(1).astype(float)
            else:
                iv = m.predict_interval(X.iloc[te])
                size = iv[:, 1] - iv[:, 0]
            nan = lambda v: float(np.mean(v)) if len(v) else np.nan
            rows.append(dict(split=s, mode=mode, coverage_all=nan(cov), coverage_seen=nan(cov[seen]),
                             coverage_new=nan(cov[~seen]), size_new=nan(size[~seen]), size_seen=nan(size[seen]),
                             seen_share=float(seen.mean()),
                             empty_new=nan((size[~seen] == 0).astype(float)) if task == "classification" else np.nan))
    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    """Mean over splits per mode."""
    return results.drop(columns="split").groupby("mode", sort=False).mean()
