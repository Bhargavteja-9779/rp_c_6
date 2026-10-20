# Pre-registered experimental protocol (frozen before the full runs)

**Freeze point:** the git commit that first adds this file. It precedes every full-mode result in
`results/`. Before the freeze, only these were run: the exploratory pilot (5 datasets, 2 models,
`research_design/pilot/`), quick-mode pipeline checks (3 datasets, 2 seeds), and one timing run
(adult, 1 seed). None of them informs the confirmatory analysis. Any later change is logged in
`protocol_deviations.md`.

## 1. Data

* **Classification:** all datasets in OpenML-CC18 (OpenML study 99) **except** the four raw-pixel
  image datasets (mnist_784 #554, Fashion-MNIST #40996, CIFAR_10 #40927, Devnagari-Script #40923),
  which are not tabular. That leaves 68 datasets.
* **Regression:** all 35 datasets in OpenML-CTR23 (study 353).
* Each dataset's default target is used. Rows with a missing target are dropped and the count is
  recorded. The ID / ignore attributes flagged by OpenML are dropped by the loader.
* **Size cap:** datasets with more than 30,000 rows are subsampled by **whole record groups**
  (random group order, seed 2026), keeping within-dataset duplicate structure.
* **Record key:** a 64-bit hash of the full feature vector. Missing values compare equal;
  categoricals are compared by label. The target is not part of the key. Hash collisions are
  possible in principle but negligible (< 10⁻⁹ expected per dataset).

## 2. Label-free audit (RQ1)

Per dataset: number of rows and record groups, the fraction of rows in groups of size ≥ 2,
the excess-copy fraction, the largest group, the fraction of label-conflicting groups and rows,
and the **predicted exposure** π̄ (Proposition 2, train fraction 0.6).

Analysis sets, defined **from the audit only** (no outcomes):
* **DUP**: predicted exposure π̄ ≥ 0.01. This is the confirmatory set for H1–H4.
* **CLEAN**: no duplicated rows. This is the null control.
* **LOW**: 0 < π̄ < 0.01. Reported descriptively.

## 3. Splits

* **Protocol R** (standard practice): uniform random row partition 60/20/20 into train,
  calibration and test.
* **Protocol G** (group-aware): whole record groups in random order, assigned to train until
  ≥ 60% of rows, then calibration up to 80%, and the rest to test.
* Seeds 0–9: ten independent repetitions per dataset, protocol and model.
* **Taxonomy:** a calibration or test row is *seen* if its key occurs among the training rows,
  otherwise *novel*.

## 4. Learners (fixed hyperparameters, no tuning)

Defaults are fixed in advance because the object of study is the validity of uncertainty
quantification, not accuracy. Tuning would need nested resampling inside the training rows and
would not change the mechanism. Capacity is varied explicitly in Experiment F.

| Name | Classification | Regression | Preprocessing (fitted on training rows only) |
|---|---|---|---|
| logreg | L2 logistic regression, C = 1 | Ridge, α = 1 | median imputation + missing indicators, standardization, one-hot (≤ 20 levels) |
| rf | Random forest, 200 trees, min_samples_leaf = 1 | same | ordinal-coded categoricals, native NaN handling |
| lgbm | LightGBM, 300 trees, learning rate 0.05, 31 leaves | same | as rf |
| knn | k-NN, k = 5 | same | as logreg |
| mlp | MLP (128, 64), Adam, early stopping | same, standardized target | as logreg |
| cqr | — | two LightGBM quantile models (0.05, 0.95), α = 0.1 only | as rf |

## 5. Conformal methods and scores

* Scores: classification uses **LAC** (1 − p̂_y) and **randomized APS** (one U per example). APS
  is randomized because the deterministic variant gives near-trivial sets for binary tasks; this
  was decided during pipeline verification, before the freeze. Regression uses the **absolute
  residual** for all five learners, plus **CQR**.
* α ∈ {0.05, 0.10, 0.20}; **primary α = 0.10**.
* Methods:
  * **SCP**: standard split CP (marginal threshold). Used with protocols R and G.
  * **MCP**: novelty-Mondrian CP, with separate thresholds for seen and novel rows. Protocol R.
  * **DCP** (exploratory): Mondrian over six bins (seen, plus quintiles of nearest-training-row
    distance for novel rows). Bin edges come from leave-one-out NN distances within the training
    set. Distances use the standardized/one-hot representation. Skipped when brute-force NN cost
    exceeds 5 × 10¹⁰ operations.
* If a group has too few calibration rows (index ⌈(n+1)(1−α)⌉ > n), its threshold is +∞
  (trivial set or infinite interval). Its frequency is recorded.

## 6. Outcomes

For every dataset × seed × protocol × learner × score × α × method:
* coverage on all, seen and novel test rows
* mean set size (classification) or interval width normalized by the training-target SD
  (regression), on all, seen and novel rows
* counts of seen/novel calibration and test rows, thresholds, fallback indicators

Calibration (classification, protocol R and G): accuracy, mean top-label confidence, **top-label
ECE** (15 equal-width bins) on all, seen and novel rows. Because ECE is biased upward on small
samples, the confirmatory calibration comparison uses (i) **overconfidence** = mean confidence −
accuracy, an unbiased signed quantity, and (ii) ECE on novel rows vs ECE on a **size-matched
random subset** of all test rows (20 draws).

## 7. Experiments

* **A/B/C (main grid):** everything above, on all included datasets.
* **D (dose–response, injection):** CLEAN datasets with ≥ 1,000 rows (randomly capped at 10,000
  rows). Append one exact copy of a random ρ-fraction of rows, ρ ∈ {0, 0.1, 0.25, 0.5, 1.0};
  protocol R; learners logreg, rf, lgbm, knn; LAC or absolute residual; α = 0.1; seeds 0–4. This
  manipulates real data synthetically and is reported as such.
* **E (exploratory near-duplicates):** coverage of SCP and DCP by distance bin.
* **F (capacity):** datasets with predicted exposure ≥ 0.05; kNN with k ∈ {1, 5, 25, 100}, RF with
  min_samples_leaf ∈ {1, 5, 25, 100}, logreg/ridge with C ∈ {100, 1, 0.01} (ridge α ∈ {0.01, 1,
  100}); LAC or absolute residual; α = 0.1; seeds 0–4.
* **G (cost):** run time of the audit and of MCP versus SCP, measured separately.

## 8. Statistical analysis plan

* **Unit of analysis = dataset.** Metrics are first averaged over seeds within dataset × learner ×
  score × α × method, so seeds and rows are never treated as independent observations. Seeds with
  no novel test rows contribute nothing to novel metrics.
* **H1 (primary, confirmatory):** in DUP at α = 0.1 under SCP-R, the per-dataset novel gap
  g = cov_novel − 0.90. For each family (task × learner × score: 10 classification families, 6
  regression families), apply a one-sided Wilcoxon signed-rank test (H₁: median g < 0), with
  **Holm** correction across the 16 families. Effect sizes: median g with a bootstrap 95% CI
  (10,000 resamples of datasets), and the share of datasets with g < −0.01.
* **H1a:** Spearman correlation between observed exposure and g, per family. Also the fraction of
  the memorization-limit gap reached: (0.9 − c_N) / (0.9 − (1 − 0.1/(1 − π))).
* **H1b:** Friedman test across the five learners on per-dataset g (classification-LAC and
  regression-absres), followed by pairwise Wilcoxon tests with Holm correction.
* **H2:** paired one-sided Wilcoxon (MCP-R novel coverage > SCP-R novel coverage) per family, with
  Holm correction, plus a non-inferiority check: the bootstrap 95% CI of the median MCP novel gap
  must lie above −0.01. Datasets where the MCP novel threshold falls back to +∞ are kept
  (coverage 1) and their number is reported.
* **H3:** two-sided Wilcoxon tests on novel, seen and overall set size / width (MCP vs SCP).
  Medians of the ratios are reported.
* **H4:** one-sided Wilcoxon tests that novel-row overconfidence > all-row overconfidence and that
  novel ECE > size-matched ECE, per learner, with Holm correction across learners.
* **H5:** Experiment D: Spearman correlation between ρ and the gap within each dataset × learner,
  then a Wilcoxon test of the correlations against 0, and the observed gap compared with the
  memorization-limit prediction. Experiment F: the same, with capacity level instead of ρ.
* **H6:** median coverage of SCP-G on its test rows, with a bootstrap CI; non-inferiority margin
  0.01.
* **Null control:** in CLEAN, SCP-R coverage and the MCP − SCP difference (identical by
  construction when no row is seen).
* Secondary α levels (0.05, 0.2) are reported descriptively, with the same tests flagged as
  secondary.
* All p-values are exact or normal-approximation Wilcoxon from SciPy and are reported exactly.
  Significance threshold: 0.05 after Holm.

## 9. Reporting rules

All datasets, seeds and learners are reported, including failures (errors are written to the raw
files). No seed or dataset selection by outcome. Negative findings are reported.
