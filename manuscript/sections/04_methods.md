# Experimental design

The protocol below was written and committed to version control before any full-scale run (it was not lodged in an external registry). Deviations and post-hoc analyses are listed in Online Resource 1 (Table S2).

## Data

We used two curated OpenML benchmark suites (Vanschoren et al. 2014): OpenML-CC18 for classification (Bischl et al. 2021) and OpenML-CTR23 for regression (Fischer et al. 2023). Four raw-pixel image datasets in CC18 (mnist_784, Fashion-MNIST, CIFAR_10, Devnagari-Script) were excluded as non-tabular, leaving {{n_cls}} classification and {{n_reg}} regression datasets. Each dataset's default target was used. Datasets with more than 30,000 rows ({{n_subsampled}} datasets) were subsampled by whole record groups, which preserves their duplicate structure. A record key was computed as a 64-bit hash of the complete feature vector; missing values compare equal, and the target is not part of the key.

A label-free audit recorded, per dataset, the share of rows belonging to a group of size at least two, the share of rows in label-conflicting groups, and the predicted exposure $\bar\pi$ of Proposition 2. The confirmatory analysis set (DUP, $\bar\pi\ge 0.01$) and the null-control set (CLEAN, no duplicated rows) were defined from this audit alone, before any outcome was computed.

## Learners, scores and conformal methods

Five learners with fixed, commonly used hyperparameters were trained: L2-regularized logistic regression (ridge regression for regression tasks), random forest (200 trees; Breiman 2001), LightGBM (300 trees, learning rate 0.05, 31 leaves; Ke et al. 2017), $k$-nearest neighbours ($k=5$) and a two-layer perceptron (128 and 64 units, early stopping). Hyperparameters were deliberately not tuned. The object of study is the validity of uncertainty quantification, and model capacity is varied explicitly in a separate experiment. All preprocessing (imputation, standardization, one-hot encoding) was fitted on training rows only (Pedregosa et al. 2011).

For classification we used the LAC score $1-\hat p_y$ (Sadinle et al. 2019) and randomized APS (Romano et al. 2020a). For regression we used the absolute residual $|y-\hat y|$ for every learner, and CQR with LightGBM quantile models at levels 0.05 and 0.95 (Romano et al. 2019). The miscoverage level was $\alpha=0.1$ (primary), with $\alpha\in\{0.05,0.2\}$ as secondary analyses (CQR at $\alpha=0.1$ only). Three methods were compared:

* **Split CP, random split (SCP-R)**, standard practice. Rows are split uniformly at random into 60% training, 20% calibration and 20% test rows, and one marginal threshold is used.
* **Novelty-Mondrian CP (MCP-R)**, the same split with separate thresholds for seen and novel rows (Proposition 3).
* **Split CP, group split (SCP-G)**. Whole record groups are assigned to the three partitions in random order, so every test row is novel.

Each configuration was repeated for ten random splits (seeds 0–9).

## Outcomes and statistical analysis

The primary outcome is the **novel-record coverage gap**, the coverage on novel test rows minus $1-\alpha$. Secondary outcomes are coverage on seen rows and on all rows, average set size (classification) or interval width divided by the standard deviation of the training targets (regression), and the frequency of the trivial-set fallback. For classifiers we also recorded accuracy and top-label calibration on seen and novel test rows. Because the expected calibration error (ECE; Naeini et al. 2015; Guo et al. 2017) is biased upwards in small samples, calibration was compared using the signed *overconfidence* (mean confidence minus accuracy), and novel-row ECE was compared against the ECE of size-matched random subsets of all test rows.

The unit of analysis is the dataset: every metric was first averaged over the ten splits. Hypothesis H1 (novel-record under-coverage under SCP-R) was tested per family (task × learner × score; 16 families) with one-sided Wilcoxon signed-rank tests (Wilcoxon 1945) and Holm correction across families (Holm 1979). Effect sizes are medians with bootstrap 95% confidence intervals (10,000 resamples of datasets). The comparison of MCP-R with SCP-R (H2) used paired one-sided Wilcoxon tests, together with a non-inferiority criterion: the bootstrap confidence interval of the median MCP-R novel gap must lie above $-0.01$. Differences between learners were assessed with Friedman tests (Friedman 1937) and Holm-corrected pairwise Wilcoxon tests. Spearman correlations for H1a are reported per family without multiplicity correction.

## Controlled experiments

**Dose–response (injection).** For every CLEAN dataset with at least 1,000 rows (randomly capped at 10,000 rows), we appended one exact copy of a random fraction $\rho\in\{0,0.1,0.25,0.5,1\}$ of the rows, then ran SCP-R and MCP-R at $\alpha=0.1$ with four learners and five seeds. This manipulates real data synthetically and isolates duplication as the cause.

**Capacity.** On datasets with $\bar\pi\ge 0.05$, we varied the flexibility of three learners: $k\in\{1,5,25,100\}$ for $k$-NN, minimum leaf size $\in\{1,5,25,100\}$ for random forests, and regularization $C\in\{100,1,0.01\}$ (ridge $\lambda\in\{0.01,1,100\}$) for linear models. Again $\alpha=0.1$ with five seeds.

**Near-duplicates (exploratory).** Novel test rows were binned by quintiles of their distance to the nearest training row, in the standardized feature space. The bin edges came from leave-one-out nearest-neighbour distances within the training set, so the taxonomy depends on training data only. We report split-CP coverage per bin and a six-bin Mondrian variant (Boström and Johansson 2020). This analysis was not part of the confirmatory hypotheses.

**Computational cost.** On the five largest datasets of each suite (30,000 rows), we timed the record hashing, the audit, the seen/novel taxonomy and the threshold computation of split CP and novelty-Mondrian CP (median of 5 repetitions on one CPU core).
