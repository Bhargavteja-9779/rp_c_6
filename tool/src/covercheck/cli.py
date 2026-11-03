"""Command line: ``covercheck data.csv --target label [--html report.html]``."""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

from .check import check
from .evaluate import evaluate, summarize
from .report import html_report


def default_model(task: str, X: pd.DataFrame, name: str = "rf", seed: int = 0):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OrdinalEncoder
    cat = [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([("num", SimpleImputer(strategy="median"), num),
                             ("cat", make_pipeline(SimpleImputer(strategy="constant", fill_value="<NA>"),
                                                   OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)), cat)])
    if name == "rf":
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        est = (RandomForestClassifier if task == "classification" else RandomForestRegressor)(n_estimators=200, n_jobs=-1,
                                                                                               random_state=seed)
    elif name == "lgbm":
        import lightgbm as lgb
        est = (lgb.LGBMClassifier if task == "classification" else lgb.LGBMRegressor)(n_estimators=300, verbose=-1,
                                                                                      random_state=seed)
    elif name == "linear":
        from sklearn.linear_model import LogisticRegression, Ridge
        from sklearn.preprocessing import StandardScaler
        est = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000) if task == "classification" else Ridge())
    else:
        raise ValueError(f"unknown model {name}")
    pipe = make_pipeline(pre, est)
    return pipe


def infer_task(y: pd.Series) -> str:
    """Classification for text, boolean or integer targets with at most 20 distinct values."""
    if pd.api.types.is_bool_dtype(y) or not pd.api.types.is_numeric_dtype(y):
        return "classification"
    if pd.api.types.is_integer_dtype(y) and y.nunique() <= 20:
        return "classification"
    return "regression"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="covercheck", description="Check, fix and report conformal coverage for new cases "
                                 "in tabular data with repeated rows.")
    ap.add_argument("data", help="CSV or Parquet file")
    ap.add_argument("--target", required=True, help="name of the target column")
    ap.add_argument("--task", choices=["auto", "classification", "regression"], default="auto")
    ap.add_argument("--alpha", type=float, default=0.1, help="miscoverage level (0.1 = 90%% coverage)")
    ap.add_argument("--model", choices=["rf", "lgbm", "linear"], default="rf")
    ap.add_argument("--splits", type=int, default=5, help="random splits for the report (0 = check only)")
    ap.add_argument("--distance", action="store_true", help="also evaluate the distance-based fix (near-copies)")
    ap.add_argument("--html", help="write a self-contained HTML report to this path")
    ap.add_argument("--json", help="write the check and the coverage summary as JSON to this path")
    ap.add_argument("--seed", type=int, default=0, help="first random seed of the splits and the model")
    a = ap.parse_args(argv)
    df = pd.read_parquet(a.data) if a.data.endswith(".parquet") else pd.read_csv(a.data)
    df = df[df[a.target].notna()].reset_index(drop=True)
    y_raw = df.pop(a.target)
    task = infer_task(y_raw) if a.task == "auto" else a.task
    chk = check(df, y_raw, alpha=a.alpha)
    print(f"Task: {task}\n" + chk.summary())
    summ = None
    if a.splits > 0:
        y = y_raw.astype(str).to_numpy() if task == "classification" else y_raw.astype(float).to_numpy()
        modes = ("standard", "exact") + (("distance",) if a.distance else ())
        res = evaluate(default_model(task, df, a.model, a.seed), df, y, task, a.alpha, a.splits, modes=modes,
                       random_state=a.seed)
        summ = summarize(res)
        with pd.option_context("display.float_format", "{:.3f}".format):
            print(summ[["coverage_all", "coverage_seen", "coverage_new", "size_new", "seen_share"]].to_string())
    if a.json:
        import json
        out = dict(data=a.data, task=task, check={k: v for k, v in chk.__dict__.items()},
                   summary=None if summ is None else summ.reset_index().to_dict("records"))
        json.dump(out, open(a.json, "w"), indent=1, default=float)
    if a.html:
        open(a.html, "w", encoding="utf8").write(html_report(a.data, chk, summ, task))
        print(f"report written to {a.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
