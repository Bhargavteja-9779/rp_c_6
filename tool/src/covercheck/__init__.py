"""covercheck: check, fix and report conformal coverage for new cases in tabular data with repeated rows.

>>> from covercheck import check, SeenNewConformal
>>> print(check(X, y).summary())                     # 1. check (no model needed)
>>> cp = SeenNewConformal(model, "classification").fit(X_tr, y_tr).calibrate(X_cal, y_cal)
>>> sets = cp.predict_set(X_new)                     # 2. fix
>>> evaluate(model, X, y)                            # 3. report coverage on seen and new cases
"""
from .check import CheckResult, check, exposures, predicted_gap, row_keys
from .conformal import SeenNewConformal
from .evaluate import evaluate, summarize
from .report import html_report

__all__ = ["check", "CheckResult", "exposures", "predicted_gap", "row_keys", "SeenNewConformal", "evaluate",
           "summarize", "html_report"]
__version__ = "0.1.0"
