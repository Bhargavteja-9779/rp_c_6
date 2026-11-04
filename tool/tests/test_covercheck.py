import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from covercheck import SeenNewConformal, check, evaluate, exposures, html_report, predicted_gap, summarize
from covercheck.cli import main as cli_main


def make_dup_data(n=1500, dup_frac=0.6, seed=0, task="classification"):
    """Data where a share of rows are exact, label-consistent copies of other rows."""
    rng = np.random.default_rng(seed)
    n0 = int(n * (1 - dup_frac))
    X0 = rng.normal(size=(n0, 5))
    y0 = (X0[:, 0] + 0.8 * rng.normal(size=n0) > 0).astype(int) if task == "classification" else \
        X0[:, 0] + 0.8 * rng.normal(size=n0)
    idx = rng.integers(0, n0, n - n0)
    X = pd.DataFrame(np.vstack([X0, X0[idx]]), columns=list("abcde"))
    y = np.concatenate([y0, y0[idx]])
    return X, y


def test_exposure_closed_form_matches_simulation():
    X, y = make_dup_data(800, 0.5)
    from covercheck.check import row_keys
    keys = row_keys(X)
    pi, pi_p = exposures(keys, y, 0.6)
    sims = []
    for s in range(300):
        perm = np.random.default_rng(s).permutation(len(y))
        tr, te = perm[:480], perm[640:]
        tk = pd.DataFrame({"k": keys[tr], "y": y[tr]})
        lab = tk.groupby("k")["y"].agg(["nunique", "first"])
        seen = np.isin(keys[te], lab.index)
        pure = np.array([k in lab.index and lab.loc[k, "nunique"] == 1 and lab.loc[k, "first"] == yy
                         for k, yy in zip(keys[te], y[te])])
        sims.append((seen.mean(), pure.mean()))
    m = np.mean(sims, 0)
    assert abs(pi - m[0]) < 0.01 and abs(pi_p - m[1]) < 0.01


def test_predicted_gap():
    assert predicted_gap(0.0, 0.1) == 0
    assert predicted_gap(0.5, 0.1) == pytest.approx(-0.1)
    assert predicted_gap(0.95, 0.1) == -0.9


def test_check_verdicts():
    X, y = make_dup_data(1000, 0.7)
    assert check(X, y).verdict.startswith("FIX RECOMMENDED")
    rng = np.random.default_rng(1)
    Xc = pd.DataFrame(rng.normal(size=(1000, 4)))
    assert check(Xc, rng.integers(0, 2, 1000)).verdict.startswith("NO ACTION")
    # many repeats but the copies disagree on the label (10 classes, groups of 5) -> advised, not recommended
    Xr = pd.DataFrame(np.repeat(rng.normal(size=(200, 3)), 5, axis=0))
    assert check(Xr, rng.integers(0, 10, 1000)).verdict.startswith("FIX ADVISED")


@pytest.mark.parametrize("task", ["classification", "regression"])
def test_fix_restores_new_case_coverage(task):
    X, y = make_dup_data(3000, 0.6, seed=3, task=task)
    est = RandomForestClassifier(100, random_state=0) if task == "classification" else RandomForestRegressor(100, random_state=0)
    # ~150 new test rows per split: the per-split SD is ~4 pp, so 12 splits give a SE of ~1.2 pp
    s = summarize(evaluate(est, X, y, task, alpha=0.1, n_splits=12, modes=("standard", "exact")))
    assert s.loc["exact", "coverage_new"] >= 0.86
    assert s.loc["standard", "coverage_new"] < s.loc["exact", "coverage_new"] - 0.03


def test_distance_mode_and_margin():
    X, y = make_dup_data(2000, 0.5, seed=5)
    est = RandomForestClassifier(100, random_state=0)
    s = summarize(evaluate(est, X, y, "classification", 0.1, n_splits=4, modes=("distance",)))
    assert s.loc["distance", "coverage_new"] >= 0.86
    cp = SeenNewConformal(RandomForestClassifier(50, random_state=0), delta=0.1).fit(X[:1200], y[:1200])
    cp.calibrate(X[1200:1600], y[1200:1600])
    assert set(cp.thresholds_) == {0, 1}
    assert cp.predict_set(X[1600:]).shape == (400, 2)


def test_full_set_when_too_few_new_calibration_rows():
    X, y = make_dup_data(400, 0.5)
    cp = SeenNewConformal(RandomForestClassifier(20, random_state=0)).fit(X, y)
    cp.calibrate(X.iloc[:5], y[:5])  # every calibration row is seen -> no new calibration rows
    assert np.isinf(cp.thresholds_[0])


def test_cli_and_report(tmp_path):
    X, y = make_dup_data(600, 0.6)
    df = X.assign(label=y)
    p = tmp_path / "d.csv"
    df.to_csv(p, index=False)
    out = tmp_path / "r.html"
    js = tmp_path / "r.json"
    assert cli_main([str(p), "--target", "label", "--splits", "2", "--html", str(out), "--json", str(js)]) == 0
    import json
    assert json.loads(js.read_text())["summary"][0]["mode"] == "standard"
    txt = out.read_text()
    assert "CoverCheck report" in txt and "<svg" in txt


def test_infer_task():
    from covercheck.cli import infer_task
    assert infer_task(pd.Series([True, False, True])) == "classification"
    assert infer_task(pd.Series(["a", "b"])) == "classification"
    assert infer_task(pd.Series([0, 1, 2, 1])) == "classification"
    assert infer_task(pd.Series(np.linspace(0, 1, 50))) == "regression"


def test_distance_bands_do_not_depend_on_calibration_data():
    X, y = make_dup_data(1500, 0.5, seed=7)
    cp = SeenNewConformal(RandomForestClassifier(30, random_state=0), mode="distance").fit(X[:900], y[:900])
    e0 = cp._edges.copy()
    cp.calibrate(X[900:1200], y[900:1200])
    e1 = cp._edges.copy()
    cp.calibrate(X[1200:], y[1200:])
    assert np.allclose(e0, e1) and np.allclose(e1, cp._edges)


def test_classwise_covers_rare_class_among_new_cases():
    rng = np.random.default_rng(11)
    n0 = 1500
    X0 = rng.normal(size=(n0, 4))
    y0 = (X0[:, 0] + 0.6 * rng.normal(size=n0) > 1.9).astype(int)       # rare positive class (~4%)
    idx = rng.integers(0, n0, 2000)
    X = pd.DataFrame(np.vstack([X0, X0[idx]]), columns=list("abcd"))
    y = np.concatenate([y0, y0[idx]])
    cov = {}
    for cw in (False, True):
        hits = []
        for s in range(4):
            perm = np.random.default_rng(s).permutation(len(y))
            tr, ca, te = perm[:2100], perm[2100:2800], perm[2800:]
            cp = SeenNewConformal(RandomForestClassifier(100, random_state=s), classwise=cw).fit(X.iloc[tr], y[tr])
            cp.calibrate(X.iloc[ca], y[ca])
            m = (~cp.is_seen(X.iloc[te])) & (y[te] == 1)
            hits.append(cp.covered(X.iloc[te][m], y[te][m]).mean() if m.any() else np.nan)
        cov[cw] = np.nanmean(hits)
    assert cov[True] >= 0.85 and cov[True] > cov[False]
