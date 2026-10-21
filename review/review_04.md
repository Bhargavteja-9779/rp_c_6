# Review 04 — Methodology and implementation

This is a distinct adversarial pass carried out by the same AI system in a different reviewer role. It was **not** conducted by independent human reviewers.

## R4.1 [MODERATE]

**Concern.** Ties: the upper coverage bound fails with tied scores (k-NN probabilities, duplicate calibration rows, discrete regression targets). Several results (k-NN/LAC, KDD Cup'99) show over-coverage.

**Response / action.** Lemma/Prop. 1 text states that ties preserve the lower bound only. Results explain the k-NN/LAC and KDD over-coverage. The decomposition in Proposition 1 is exact regardless of ties.

**Files / experiments.** 03_theory.md, 05_results.md

**Status.** Fixed

## R4.2 [MINOR]

**Concern.** Novelty is defined on raw feature keys, whereas models see preprocessed features (infrequent categories merged), so some 'novel' rows are identical in model space.

**Response / action.** Makes the analysis conservative (fewer seen rows). Noted in data_leakage_audit.md.

**Files / experiments.** —

**Status.** Disclosed

## R4.3 [MINOR]

**Concern.** Equation and code consistency.

**Response / action.** Checked: conformal_quantile implements ⌈(n+1)(1−α)⌉ with +∞ fallback; Mondrian uses per-group quantiles; APS randomization matches Romano et al. (2020a); exposure formula matches the hypergeometric expression and passes the simulation unit test.

**Files / experiments.** tests/test_core.py

**Status.** Verified
