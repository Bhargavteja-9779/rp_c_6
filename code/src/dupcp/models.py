"""Learners and leakage-safe preprocessing (all transformers are fitted on training rows only)."""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

MODELS = ("logreg", "rf", "lgbm", "knn", "mlp")


def _columns(X: pd.DataFrame):
    num = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    cat = [c for c in X.columns if c not in num]
    return num, cat


def dense_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Standardized numerics (+ missing indicators) and one-hot categoricals."""
    num, cat = _columns(X)
    steps = []
    if num:
        steps.append(("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True,
                                                         keep_empty_features=True),
                                           StandardScaler()), num))
    if cat:
        steps.append(("cat", make_pipeline(SimpleImputer(strategy="most_frequent", keep_empty_features=True),
                                           OneHotEncoder(handle_unknown="infrequent_if_exist",
                                                         max_categories=20)), cat))
    return ColumnTransformer(steps, sparse_threshold=0.3)


def tree_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Ordinal-coded categoricals; numerics passed through with NaN (handled natively)."""
    num, cat = _columns(X)
    steps = []
    if num:
        steps.append(("num", "passthrough", num))
    if cat:
        steps.append(("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1,
                                            encoded_missing_value=np.nan), cat))
    return ColumnTransformer(steps)


def _prep_cat_strings(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for c in X.columns:
        if not pd.api.types.is_numeric_dtype(X[c]):
            X[c] = X[c].astype("object").where(X[c].notna(), np.nan)
            X[c] = X[c].map(lambda v: v if (isinstance(v, float) and np.isnan(v)) else str(v))
    return X


def make_model(name: str, task: str, X: pd.DataFrame, seed: int, **kw):
    clf = task == "classification"
    if name == "logreg":
        est = LogisticRegression(C=kw.get("C", 1.0), max_iter=2000) if clf else Ridge(alpha=kw.get("alpha", 1.0))
        return make_pipeline(dense_preprocessor(X), est)
    if name == "knn":
        k = kw.get("k", 5)
        est = KNeighborsClassifier(n_neighbors=k) if clf else KNeighborsRegressor(n_neighbors=k)
        return make_pipeline(dense_preprocessor(X), est)
    if name == "mlp":
        if clf:
            est = MLPClassifier(hidden_layer_sizes=(128, 64), early_stopping=True, max_iter=200,
                                random_state=seed)
        else:
            est = TransformedTargetRegressor(
                regressor=MLPRegressor(hidden_layer_sizes=(128, 64), early_stopping=True, max_iter=200,
                                       random_state=seed),
                transformer=StandardScaler())
        return make_pipeline(dense_preprocessor(X), est)
    if name == "rf":
        p = dict(n_estimators=200, min_samples_leaf=kw.get("min_samples_leaf", 1), n_jobs=1,
                 random_state=seed)
        est = RandomForestClassifier(**p) if clf else RandomForestRegressor(**p)
        return make_pipeline(tree_preprocessor(X), est)
    if name == "lgbm":
        from lightgbm import LGBMClassifier, LGBMRegressor
        p = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, n_jobs=1, verbose=-1,
                 random_state=seed)
        est = LGBMClassifier(**p) if clf else LGBMRegressor(**p)
        return make_pipeline(tree_preprocessor(X), est)
    if name in ("lgbm_q_lo", "lgbm_q_hi"):
        from lightgbm import LGBMRegressor
        q = kw["quantile"]
        est = LGBMRegressor(objective="quantile", alpha=q, n_estimators=300, learning_rate=0.05,
                            num_leaves=31, n_jobs=1, verbose=-1, random_state=seed)
        return make_pipeline(tree_preprocessor(X), est)
    raise ValueError(name)


def fit_predict(name, task, X_tr, y_tr, X_eval_list, seed, n_classes=None, **kw):
    """Fit on training rows; return class-probability matrices (K columns) or point predictions."""
    X_tr = _prep_cat_strings(X_tr)
    X_eval_list = [_prep_cat_strings(X) for X in X_eval_list]
    m = make_model(name, task, X_tr, seed, **kw)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(X_tr, y_tr)
        outs = []
        for Xe in X_eval_list:
            if task == "classification":
                P = m.predict_proba(Xe)
                full = np.zeros((len(Xe), n_classes))
                full[:, m.classes_.astype(int)] = P
                outs.append(full)
            else:
                outs.append(np.asarray(m.predict(Xe), dtype=float))
    return outs


def dense_features(X_tr: pd.DataFrame, X_other: list[pd.DataFrame]):
    """Standardized/one-hot representation (fitted on training rows) for distance computations."""
    X_tr = _prep_cat_strings(X_tr)
    ct = dense_preprocessor(X_tr)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        Z_tr = ct.fit_transform(X_tr)
        Z_o = [ct.transform(_prep_cat_strings(X)) for X in X_other]
    return Z_tr, Z_o
