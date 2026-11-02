"""Step 1, *check*: predict from the data alone (no model, no training) how much a random split can
overstate conformal coverage for new cases."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.special import gammaln


def row_keys(X) -> np.ndarray:
    """64-bit hash of each row's full feature vector (NaN equals NaN; categories compared by value)."""
    Z = pd.DataFrame(X).copy()
    Z.columns = [str(c) for c in Z.columns]
    for c in Z.columns:
        if pd.api.types.is_numeric_dtype(Z[c]) and not pd.api.types.is_bool_dtype(Z[c]):
            Z[c] = Z[c].astype("float64")
        else:
            Z[c] = Z[c].astype("string").fillna("<NA>")
    return pd.util.hash_pandas_object(Z, index=False).to_numpy(dtype=np.uint64)


def _ratio(N1, k, n):
    """C(N1 - k, n) / C(N1, n): probability that a random n-subset of N1 items avoids k given items."""
    k = np.asarray(k, dtype=float)
    out = np.zeros_like(k)
    ok = N1 - k >= n
    out[ok] = np.exp(gammaln(N1 - k[ok] + 1) - gammaln(N1 - k[ok] - n + 1) - gammaln(N1 + 1) + gammaln(N1 - n + 1))
    return out


def exposures(keys: np.ndarray, y, train_frac: float = 0.6) -> tuple[float, float]:
    """Expected share of test rows that are *seen* (pi_bar, Eq. 2) and *label-pure seen* (pi_P_bar).

    A test row is label-pure seen if at least one training row has the same features and every such
    training row has exactly the test row's label (or target value). Both are exact expectations
    over uniformly random splits with round(train_frac * N) training rows.
    """
    keys = np.asarray(keys)
    y = pd.Series(np.asarray(y)).astype("string").fillna("<NA>").to_numpy()
    N = len(keys)
    nT = int(round(train_frac * N))
    df = pd.DataFrame({"k": keys, "y": y})
    m = df.groupby("k")["k"].transform("size").to_numpy()
    m_same = df.groupby(["k", "y"])["k"].transform("size").to_numpy()
    p_none = _ratio(N - 1, m - 1, nT)            # no copy of the row in training
    p_no_diff = _ratio(N - 1, m - m_same, nT)    # no copy with a different label in training
    return float(np.mean(1 - p_none)), float(np.mean(p_no_diff - p_none))


def predicted_gap(pi_p: float, alpha: float) -> float:
    """Worst-case coverage gap for new cases (Eq. 3): -alpha * pi_P / (1 - pi_P)."""
    return -(1 - alpha) if pi_p >= 1 - alpha else -alpha * pi_p / (1 - pi_p)


@dataclass
class CheckResult:
    n_rows: int
    repeated_row_share: float
    exposure: float
    pure_exposure: float
    predicted_gap: float
    exposure_only_gap: float
    alpha: float
    verdict: str
    reasons: list[str] = field(default_factory=list)

    def summary(self) -> str:
        pp = lambda g: f"{100 * g:+.1f} pp"
        return (f"Rows: {self.n_rows:,} | rows with an identical copy: {100 * self.repeated_row_share:.1f}%\n"
                f"Expected share of test rows seen in training: {100 * self.exposure:.1f}%\n"
                f"  ... of which the copies agree on the label: {100 * self.pure_exposure:.1f}%\n"
                f"Predicted worst-case coverage gap for new cases: {pp(self.predicted_gap)} "
                f"(target {100 * (1 - self.alpha):.0f}%)\n"
                f"VERDICT: {self.verdict}\n" + "".join(f"  - {r}\n" for r in self.reasons))


def check(X, y, alpha: float = 0.1, train_frac: float = 0.6, gap_tol: float = 0.02,
          exposure_tol: float = 0.10) -> CheckResult:
    """Run the check. Flags the data if the predicted gap is worse than -gap_tol or if more than
    exposure_tol of test rows are expected to be seen (the combined rule of the paper)."""
    keys = row_keys(X)
    _, inv, cnt = np.unique(keys, return_inverse=True, return_counts=True)
    pi, pi_p = exposures(keys, y, train_frac)
    g, g_pi = predicted_gap(pi_p, alpha), predicted_gap(pi, alpha)
    reasons = []
    if g < -gap_tol:
        reasons.append(f"{100 * pi_p:.0f}% of test rows will have a training copy with the same label; a model "
                       f"that memorizes them can miss new cases {100 * alpha / (1 - min(pi_p, 0.999)):.0f}% of the time "
                       f"instead of {100 * alpha:.0f}%.")
    if pi >= exposure_tol:
        reasons.append(f"{100 * pi:.0f}% of test rows will be seen in training; report coverage on new cases "
                       "separately.")
    if g < -gap_tol:
        verdict = "FIX RECOMMENDED: calibrate seen and new cases separately (SeenNewConformal)."
    elif pi >= exposure_tol:
        verdict = "FIX ADVISED: many repeats; the risk is lower because repeats disagree on the label, but the fix costs little."
    else:
        verdict = "NO ACTION NEEDED: standard split conformal prediction is adequate for new cases."
        reasons.append("Few repeated rows; seen test rows cannot distort the coverage estimate much.")
    return CheckResult(len(keys), float(np.mean(cnt[inv] > 1)), pi, pi_p, g, g_pi, alpha, verdict, reasons)
