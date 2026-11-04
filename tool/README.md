# covercheck

**Check, fix and report conformal prediction coverage for new cases in tabular data with repeated rows.**

Conformal prediction promises that its prediction sets contain the true answer, say, 90% of the
time. People usually confirm this on a random test split. When the data contain repeated rows,
many test rows have an exact copy in the training data. The check then averages over easy repeats
and genuinely new cases, and it can report 90% while new cases are covered far less often.

`covercheck` implements the three-step routine from the accompanying paper:

1. **Check.** Count repeated rows and whether the copies agree on the label, then predict the
   worst-case coverage gap for new cases. This needs no model, and the computation is exact and
   takes seconds.
2. **Fix.** `SeenNewConformal` calibrates seen and new cases separately (Mondrian conformal
   prediction), so coverage holds for new cases and for any mix of seen and new cases.
   `mode="distance"` also handles near-copies, and `delta=0.1` adds a safety margin against an
   unlucky calibration draw.
3. **Report.** `evaluate` measures coverage overall, on seen cases and on new cases, with and
   without the fix, and the CLI writes a one-page HTML report.

## Install

```bash
pip install -e .            # from this folder; optional extras: .[lgbm,parquet]
```

## Command line

```bash
covercheck examples/mc1.csv --target defective --splits 10 --html report.html
```

Output on the NASA mc1 software-defect data (`examples/mc1.csv`, 9,466 modules):

```
Rows: 9,466 | rows with an identical copy: 84.3%
Expected share of test rows seen in training: 82.0%
  ... of which the copies agree on the label: 81.2%
Predicted worst-case coverage gap for new cases: -43.3 pp (target 90%)
VERDICT: FIX RECOMMENDED: calibrate seen and new cases separately (SeenNewConformal).

          coverage_all  coverage_seen  coverage_new  size_new  seen_share
standard         0.917          0.981         0.625     0.628       0.819
exact            0.961          0.974         0.904     0.915       0.819
```

The usual check reports 91.7% coverage, but new modules are covered only 62.5% of the time, and
37% of them get an *empty* prediction set. With the fix, new modules are covered 90.4% of the time.
The HTML report is in `examples/mc1_report.html`.

## Python

```python
from covercheck import check, SeenNewConformal, evaluate, summarize
from sklearn.ensemble import RandomForestClassifier

print(check(X, y).summary())                       # 1. check, before training anything

cp = SeenNewConformal(RandomForestClassifier(), task="classification", alpha=0.1)
cp.fit(X_train, y_train).calibrate(X_cal, y_cal)   # 2. fix
sets = cp.predict_set(X_new)                       # boolean matrix: label j in the set of case i
cp.is_seen(X_new)                                  # which cases have an exact copy in the training data

print(summarize(evaluate(RandomForestClassifier(), X, y, n_splits=10)))   # 3. report
```

For regression use `task="regression"` and `predict_interval`.

For a rare class that must be covered among new cases (for example defective modules), use
`SeenNewConformal(model, classwise=True)`. This sets one threshold per seen/new group *and* per class.
Expect larger sets: the model then admits when it cannot tell.

## What the verdict means

| Verdict | Rule | What to do |
|---|---|---|
| FIX RECOMMENDED | predicted gap worse than −2 pp | Use `SeenNewConformal`, and report new-case coverage. |
| FIX ADVISED | ≥ 10% of test rows will be seen, but the copies mostly disagree on the label | Low risk for memorizing models. The fix costs little, so use it and report both numbers. |
| NO ACTION NEEDED | otherwise | Standard split conformal prediction is adequate. |

The predicted gap −α π_P / (1 − π_P) is a worst case for models that memorize their training rows.
In the paper's validation it worked as a limit and as a screen: it caught every data set where
random forests or LightGBM fell more than 2 pp short. It does not forecast the exact gap.

## Tests

```bash
pip install pytest && pytest tests
```

License: MIT.
