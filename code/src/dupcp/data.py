"""Data acquisition from OpenML and record-group (duplicate) keys.

Datasets are fetched with scikit-learn's OpenML client (ARFF parsed by pandas), which applies the
dataset's default target and drops row-id / ignore attributes. Each dataset is cached locally as
parquet so later stages do not touch the network.
"""
from __future__ import annotations

import json
import os
import urllib.request

import numpy as np
import pandas as pd

SUITES = {"classification": 99, "regression": 353}  # OpenML-CC18, OpenML-CTR23
# Raw-pixel image datasets in CC18: not tabular data (pre-registered exclusion).
EXCLUDED_IMAGE_IDS = {554, 40996, 40927, 40923}
MAX_ROWS = 30_000
# External-validation datasets whose duplicate groups exceed the cap: uniform row subsample instead
ROW_SUBSAMPLE_IDS = {1113}
EXTERNAL_IDS = [1056, 1069, 1065, 1071, 1113]
SUBSAMPLE_SEED = 2026


def suite_data_ids(study_id: int) -> list[int]:
    url = f"https://www.openml.org/api/v1/json/study/{study_id}"
    with urllib.request.urlopen(url, timeout=120) as r:
        d = json.load(r)
    return [int(i) for i in d["study"]["data"]["data_id"]]


def row_keys(X: pd.DataFrame) -> np.ndarray:
    """64-bit hash of the full feature vector; NaN compares equal to NaN.

    Categorical columns are hashed by their string value so that two rows with the same category
    label collide regardless of the categorical's code ordering.
    """
    Z = X.copy()
    for c in Z.columns:
        if not pd.api.types.is_numeric_dtype(Z[c]):
            Z[c] = Z[c].astype("string").fillna("<NA>")
        else:
            Z[c] = Z[c].astype("float64")
    return pd.util.hash_pandas_object(Z, index=False).to_numpy(dtype=np.uint64)


def group_preserving_subsample(keys: np.ndarray, max_rows: int, seed: int) -> np.ndarray:
    """Indices of a subsample made of whole record groups (keeps duplicate structure)."""
    n = len(keys)
    if n <= max_rows:
        return np.arange(n)
    uniq, inv = np.unique(keys, return_inverse=True)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(uniq))
    sizes = np.bincount(inv, minlength=len(uniq))
    chosen = np.zeros(len(uniq), dtype=bool)
    total = 0
    for g in order:
        if total + sizes[g] > max_rows:
            continue
        chosen[g] = True
        total += sizes[g]
        if total >= max_rows:
            break
    return np.flatnonzero(chosen[inv])


def load_dataset(data_id: int, task: str, cache_dir: str) -> dict:
    """Return dict(X=DataFrame, y=ndarray, keys=ndarray, name=str, n_raw=int, subsampled=bool)."""
    os.makedirs(cache_dir, exist_ok=True)
    pq = os.path.join(cache_dir, f"{data_id}.parquet")
    meta_p = os.path.join(cache_dir, f"{data_id}.json")
    if os.path.exists(pq) and os.path.exists(meta_p):
        df = pd.read_parquet(pq)
        meta = json.load(open(meta_p))
    else:
        from sklearn.datasets import fetch_openml
        b = fetch_openml(data_id=data_id, as_frame=True, parser="pandas",
                         data_home=os.path.join(cache_dir, "_sk"))
        df = b.data.copy()
        if isinstance(b.target, pd.DataFrame):
            raise ValueError(f"dataset {data_id} has multiple targets")
        df["__target__"] = b.target.values
        meta = {"name": b.details["name"], "version": b.details.get("version"),
                "target": b.details.get("default_target_attribute")}
        df.columns = [str(c) for c in df.columns]
        df.to_parquet(pq)
        json.dump(meta, open(meta_p, "w"))
    y_raw = df.pop("__target__")
    X = df
    keep = y_raw.notna().to_numpy()
    X, y_raw = X.loc[keep].reset_index(drop=True), y_raw.loc[keep].reset_index(drop=True)
    if task == "classification":
        y = pd.factorize(y_raw.astype("string"), sort=True)[0].astype(int)
    else:
        y = y_raw.astype(float).to_numpy()
    keys = row_keys(X)
    n_raw = len(y)
    if data_id in ROW_SUBSAMPLE_IDS and n_raw > MAX_ROWS:
        idx = np.sort(np.random.default_rng(SUBSAMPLE_SEED).choice(n_raw, MAX_ROWS, replace=False))
    else:
        idx = group_preserving_subsample(keys, MAX_ROWS, SUBSAMPLE_SEED)
    sub = len(idx) < n_raw
    X, y, keys = X.iloc[idx].reset_index(drop=True), y[idx], keys[idx]
    return {"X": X, "y": y, "keys": keys, "name": meta["name"], "n_raw": n_raw,
            "subsampled": sub, "dropped_missing_target": int((~keep).sum())}
