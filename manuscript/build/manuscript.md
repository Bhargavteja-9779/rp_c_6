---
title: "Seen or new? Duplicate records, conformal coverage on novel inputs, and a novelty-conditional remedy for tabular benchmarks"
---

**Abstract** Split conformal prediction guarantees that its prediction sets reach a chosen coverage level, but only on average over held-out rows. When a tabular dataset contains repeated records, a random split places exact copies of some test rows in the training set, and the guarantee then averages over rows the model has already seen and genuinely new ones. We show that coverage on new (novel) records equals $(c-\pi c_{\mathrm S})/(1-\pi)$, where $\pi$ is the share of test rows with a training copy and $c_{\mathrm S}$ the coverage of those rows. When seen rows are always covered, the error rate on new records inflates from $\alpha$ to $\alpha/(1-\pi)$. We give a label-free formula that predicts $\pi$ from duplicate-group sizes, and we prove that a novelty-Mondrian conformal predictor is valid for any mix of seen and new records. Across 103 OpenML-CC18/CTR23 datasets, five learners and four scores, predicted and observed exposure agreed closely (mean absolute error 0.0012). The pre-specified primary hypothesis that the typical duplicated dataset under-covers new records was not supported: median gaps were −0.8 to +0.5 percentage points, excluding a tie-inflated k-NN variant. Shortfalls were concentrated where exposure was high and seen records were over-covered, reaching −16.9 points, and they were reproduced in external defect-prediction and intrusion-detection data and, as a dose–response, by controlled duplicate injection. Novelty-Mondrian calibration restored nominal coverage on new records at a median set-size cost of at most 4.4%; in regression, a distance-normalized score also removed most of the shortfall, but without a guarantee.

**Keywords** Conformal prediction · Uncertainty quantification · Data leakage · Duplicate records · Tabular benchmarks · Mondrian calibration


# Introduction

Conformal prediction (CP) has become a standard way to attach uncertainty to the predictions of arbitrary machine-learning models. Given a model trained on one part of the data and a held-out calibration set, split CP returns a prediction set (classification) or an interval (regression) that contains the true label with probability at least $1-\alpha$. The guarantee holds in finite samples and requires only exchangeability (Papadopoulos et al. 2002; Lei et al. 2018; Vovk et al. 2022; Angelopoulos and Bates 2023). Methods are evaluated in the same way the guarantee is stated: rows of a benchmark dataset are randomly split into training, calibration and test parts, and the empirical coverage on the test rows is compared with $1-\alpha$.

Rows are not always distinct records. Tabular benchmarks contain repeated feature vectors, because the same event was logged twice, because the same entity was measured repeatedly, or because a coarse discrete feature space makes identical profiles recur. A recent audit (Li 2026, a preprint) found duplicated rows in about half of the datasets in widely used tabular benchmark collections, which our own audit confirms (53 of 103 datasets), and duplication is a documented quality problem of well-known datasets such as the NASA software-defect data (Gray et al. 2011; Shepperd et al. 2013). Under a random row split, some test rows then have exact copies in the training set. Duplicate leakage of this kind inflates accuracy and can change model rankings (Li 2026; Roth 2026; both preprints), but its effect on *uncertainty quantification* has not, to our knowledge, been examined. That effect is of a different kind. CP is valued because its coverage is *guaranteed*, and practitioners use the guarantee to make risk-sensitive decisions. If the reported 90% is an average over records the model has already seen and records it has not, the guarantee for new records, which are what a deployed model mostly encounters, may be weaker than the one reported.

This paper asks whether that happens, by how much, where, and how to prevent it. Our contributions are:

1. **An exact characterization.** Coverage on novel records equals $(c-\pi c_{\mathrm S})/(1-\pi)$, where $\pi$ is the share of test rows with a training copy and $c_{\mathrm S}$ their coverage. Novel records are under-covered exactly when seen records are over-covered. In the memorization limit the error rate on novel records is $\alpha/(1-\pi)$ (Proposition 1).
2. **A label-free exposure formula** that predicts $\pi$ from the sizes of duplicate groups, before any model is trained (Proposition 2).
3. **A remedy with a guarantee.** Calibrating seen and novel records separately is exactly valid for both groups, and therefore for any deployment mix of seen and new records (Proposition 3 and Corollary 1). The method is standard Mondrian CP (Vovk et al. 2022); what is new is the taxonomy, which is defined by membership of the training set, and the argument that this data-dependent taxonomy is admissible.
4. **A large-scale evaluation following a pre-specified protocol** (committed to version control before the full runs, not lodged in an external registry) on 103 datasets of the OpenML-CC18 and OpenML-CTR23 suites, with five learners, four nonconformity scores, three miscoverage levels, a group-aware split, controlled duplicate-injection and model-capacity experiments, an analysis of probability calibration, and an external validation on defect-prediction and intrusion-detection data with documented duplication.

The evidence supports a more nuanced conclusion than the pre-specified primary hypothesis. For the *typical* duplicated benchmark dataset, coverage on novel records is within about 1 percentage point of nominal, and the primary test was not significant. The shortfall is concentrated in datasets with high exposure whose seen records are over-covered. There it reaches −16.9 points in the benchmark suites and −27.5 points in the external data, as the theory predicts. By contrast, a dataset with equally high exposure but conflicting duplicate labels (cps88wages) was unaffected. Because both quantities can be audited cheaply, at-risk datasets can be identified in advance, and novelty-Mondrian calibration removes the problem at a small cost in set size. The pipeline, raw results and analysis code are released.


# Related work

## Conformal prediction and conditional validity

Split (inductive) conformal prediction (CP) turns any fitted model into set-valued predictions with finite-sample coverage, provided the calibration and test observations are exchangeable (Papadopoulos et al. 2002; Lei et al. 2018; Vovk et al. 2022). Common nonconformity scores include the least-ambiguous-set score for classification (LAC; Sadinle et al. 2019), adaptive prediction sets (APS; Romano et al. 2020a), the absolute residual for regression (Lei et al. 2018) and conformalized quantile regression (CQR; Romano et al. 2019). The guarantee is *marginal*: it averages over the joint distribution of covariates and labels. Exact coverage conditional on an arbitrary covariate value cannot be achieved without further assumptions (Vovk 2012; Foygel Barber et al. 2021). Coverage conditional on membership of finitely many pre-specified categories can be achieved, by Mondrian (category-conditional) CP (Vovk et al. 2022) or, more generally, by calibration over a function class (Gibbs et al. 2025) or multivalid calibration over overlapping groups (Bastani et al. 2022). For disjoint groups, conditional calibration reduces to Mondrian calibration. Group-conditional calibration has been used to equalize coverage across protected groups (Romano et al. 2020b), classes (Löfström et al. 2015; Ding et al. 2023) and difficulty strata (Papadopoulos et al. 2011; Boström and Johansson 2020); localized CP reweights calibration scores around a test point (Guan 2023). Mondrian-type calibration has recently been applied to spatial modelling (Seo et al. 2026) and to heteroscedastic regression with tree-based conformal predictive systems (Zhang and Zhou 2026), and conformal prediction has been examined under strong distribution shifts in drug-response modelling (Hernandez-Hernandez et al. 2026). Robustness of CP to departures from exchangeability is analysed by Tibshirani et al. (2019) and Barber et al. (2023). For data with a known grouping, e.g. repeated measurements of subjects, Dunn et al. (2023) construct prediction sets for new groups. None of these works considers the grouping that arises *implicitly* when records are duplicated, or the fact that a random split makes group membership depend on the training set.

## Duplicates, overlap and leakage in evaluation

Leakage of information from the evaluation data into training is a pervasive source of over-optimism in applied machine learning (Kaufman et al. 2012; Kapoor and Narayanan 2023). Exact and near-duplicates between training and test data have been documented for image benchmarks (Barz and Denzler 2020), language-model corpora (Lee et al. 2022), source code (Allamanis 2019) and question answering, where accuracy on test questions that overlap the training set greatly exceeds accuracy on novel ones (Lewis et al. 2021; Elangovan et al. 2021). In tabular data, duplicated and inconsistent records are a known quality problem of the NASA software-defect data (Gray et al. 2011; Shepperd et al. 2013) and of the KDD Cup'99 intrusion data (Tavallaee et al. 2009). Two recent preprints quantify the problem across benchmark collections. Li (2026) audits 156 datasets from two OpenML suites and UCI, finds at least one duplicated row in 48%, and shows that random row-level cross-validation inflates accuracy and can change the leading model. Roth (2026) shows that memorization leakage grows with model capacity. Both studies measure *point* performance. In cheminformatics, CP is used to characterise the applicability domain of models (Norinder et al. 2014), and CP calibration degrades on temporally newer compounds (Morger et al. 2021; see also Sheridan 2013). We are not aware of work that quantifies how duplicated records affect the *coverage guarantees* of conformal predictors, or the calibration of predicted probabilities, on records that the model has not seen.


# Problem formulation and theory

## Setting

Let $D=\{(x_i,y_i)\}_{i=1}^{N}$ be a data set whose rows are randomly partitioned, uniformly over all partitions of the given sizes, into a training set $T$ of $n_T$ rows, a calibration set $C$ of $n_C$ rows and a test set $E$. A *record group* is a maximal set of rows with identical feature vector; $m_g$ denotes the size of group $g$. Labels inside a group may differ. We call a calibration or test row *seen* if some training row has the same feature vector, and *novel* otherwise:
$$\kappa_T(x)=\mathrm{S}\ \text{if}\ \exists\, j\in T:\ x_j=x,\qquad \kappa_T(x)=\mathrm{N}\ \text{otherwise}.$$
The taxonomy $\kappa_T$ depends only on the training features. A model fitted on $T$ defines a nonconformity score $s(x,y)$. Split CP returns $\mathcal{C}(x)=\{y:\ s(x,y)\le\hat q\}$, where $\hat q$ is the $\lceil (n_C+1)(1-\alpha)\rceil$-th smallest calibration score ($+\infty$ if this rank exceeds $n_C$). Conditional on $T$, let $\pi$ be the probability that a randomly drawn test row is seen, $c$ the coverage of a random test row, and $c_{\mathrm S}=1-m_{\mathrm S}$ and $c_{\mathrm N}=1-m_{\mathrm N}$ the coverages of seen and novel test rows ($m$ denoting miscoverage).

**Lemma 0.** Conditional on the set of training rows, the remaining rows are assigned to $C$ and $E$ uniformly at random. Hence for any test row $j$ the rows of $C\cup\{j\}$ are exchangeable, and $\kappa_T$ is a fixed function.

Lemma 0 yields the familiar guarantee $c\ge 1-\alpha$, and $c\le 1-\alpha+\delta$ with $\delta=1/(n_C+1)$ when scores are almost surely distinct (Lei et al. 2018). Exact duplicates in $C$ produce tied scores. Ties preserve the lower bound but can break the upper one.

## How much coverage do novel records receive?

**Proposition 1.** For any model and score, conditional on $T$ with $\pi<1$,
$$c_{\mathrm N}=\frac{c-\pi c_{\mathrm S}}{1-\pi},\qquad \frac{\alpha-\delta-\pi m_{\mathrm S}}{1-\pi}\ \le\ m_{\mathrm N}\ \le\ \frac{\alpha-\pi m_{\mathrm S}}{1-\pi},$$
where the left inequality requires almost surely distinct scores.

*Proof.* By total probability, $c=\pi c_{\mathrm S}+(1-\pi)c_{\mathrm N}$, so $m_{\mathrm N}=(1-c-\pi m_{\mathrm S})/(1-\pi)$; insert $\alpha-\delta\le 1-c\le\alpha$. $\square$

Three consequences follow. First, novel records are under-covered exactly when seen records are over-covered ($m_{\mathrm S}<\alpha$), up to $\delta$. Second, in the *memorization limit* $m_{\mathrm S}\to 0$, reached when the model reproduces its training records, the novel miscoverage is $\alpha/(1-\pi)$: at $\alpha=0.1$ and $\pi=0.5$ one in five new records is missed while the reported coverage is 90%. Third, the gap $c_{\mathrm N}-(1-\alpha)\approx-\pi(\alpha-m_{\mathrm S})/(1-\pi)$ grows with the exposure $\pi$ and with the model's tendency to fit its training records. Both are testable dose–response predictions.

## Exposure can be predicted before any model is trained

**Proposition 2.** Let row $j$ belong to a group of size $m_g$. Then
$$\Pr\{\kappa_T(x_j)=\mathrm S\mid j\in E\}=1-\binom{N-m_g}{n_T}\Big/\binom{N-1}{n_T}\approx 1-(1-f)^{m_g-1},\quad f=\frac{n_T}{N-1},$$
and the expected exposure of a random test row is $\bar\pi=\sum_g (m_g/N)\,[1-\binom{N-m_g}{n_T}/\binom{N-1}{n_T}]$.

*Proof.* Given $j\in E$, the training set is a uniformly random $n_T$-subset of the other $N-1$ rows, and $x_j$ is novel exactly when none of the $m_g-1$ other copies is selected. $\square$

Combined with Proposition 1, a label-free audit of group sizes therefore yields a worst-case prediction $1-\alpha/(1-\bar\pi)$ for novel-record coverage. Li (2026) gives the analogous exposure probability for $K$-fold cross-validation.

## A remedy with a guarantee for any deployment mix

*Novelty-Mondrian CP* calibrates seen and novel rows separately. Let $C_k=\{i\in C:\kappa_T(x_i)=k\}$, $n_k=|C_k|$, and let $\hat q_k$ be the $\lceil (n_k+1)(1-\alpha)\rceil$-th smallest score in $C_k$ ($+\infty$ if that rank exceeds $n_k$). The prediction set is $\mathcal C^{\mathrm M}(x)=\{y: s(x,y)\le \hat q_{\kappa_T(x)}\}$.

**Proposition 3.** For $k\in\{\mathrm S,\mathrm N\}$, $\Pr\{Y\in\mathcal C^{\mathrm M}(X)\mid\kappa_T(X)=k,\,T\}\ge 1-\alpha$. With almost surely distinct scores the coverage is at most $1-\alpha+1/(n_k+1)$, conditional on $n_k$.

*Proof.* By Lemma 0, given $T$ the taxonomy is fixed and $C\cup\{j\}$ is exchangeable. Conditional on $\kappa_T(x_j)=k$ and on the multiset of category-$k$ rows in $C\cup\{j\}$, each of these $n_k+1$ rows is equally likely to be the test row. The usual quantile argument for Mondrian CP (Vovk et al. 2022) then applies within category $k$. $\square$

**Corollary 1.** For a deployment population that mixes seen and novel rows in any proportion $w\in[0,1]$, novelty-Mondrian CP has coverage at least $1-\alpha$. Under the same mix, split CP has coverage $w\,c_{\mathrm S}+(1-w)\,c_{\mathrm N}$, which for an all-new deployment ($w=0$) equals $c_{\mathrm N}$.

The remedy has an honest price. If fewer than $1/\alpha-1$ novel calibration rows are available, $\hat q_{\mathrm N}=+\infty$ and novel records receive the trivial set, signalling that the calibration data contain too little evidence about new records. An alternative is to split by record group, so that every test row is novel. Because groups have unequal sizes, that protocol has no row-level exchangeability guarantee, and we assess it empirically.

The analysis conditions on the finite data set. Its estimand is coverage of held-out rows, overall or restricted to rows that are novel with respect to the training set. Whether genuinely new deployment records behave like novel held-out rows is an assumption about the data-generating process, not a consequence of the theory.


# Experimental design

The protocol below was written and committed to version control before any full-scale run (it was not lodged in an external registry). Deviations and post-hoc analyses are listed in Online Resource 1 (Table S2).

## Data

We used two curated OpenML benchmark suites (Vanschoren et al. 2014): OpenML-CC18 for classification (Bischl et al. 2021) and OpenML-CTR23 for regression (Fischer et al. 2023). Four raw-pixel image datasets in CC18 (mnist_784, Fashion-MNIST, CIFAR_10, Devnagari-Script) were excluded as non-tabular, leaving 68 classification and 35 regression datasets. Each dataset's default target was used. Datasets with more than 30,000 rows (12 datasets) were subsampled by whole record groups, which preserves their duplicate structure. A record key was computed as a 64-bit hash of the complete feature vector; missing values compare equal, and the target is not part of the key.

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


# Results

All runs completed: 103 datasets × 10 splits × 2 split protocols × 5 learners, with no failed fits. Every number below is computed by the released analysis code from the per-split result files.

## Duplicates are common, and exposure is predictable from a label-free audit

Of the 103 datasets, 53 contain at least one duplicated feature vector. In 37, at least 1% of rows belong to a duplicate group, and in 11 at least 30% do. In 35 datasets some duplicate groups carry conflicting labels. The confirmatory set DUP (predicted exposure $\bar\pi\ge 0.01$) contains 24 classification and 12 regression datasets, with median predicted exposure 0.104 (maximum 0.853). In 18 of them, at least 10% of test rows are expected to have an exact training copy, and in 9 at least 30%. The CLEAN null-control set contains 32 classification and 18 regression datasets, and 17 datasets have negligible exposure. Table 1 summarizes the audit; the statistics for every dataset are listed in Online Resource 1 (Table S1).

**Table 1** Label-free duplicate audit by task and analysis set (medians over datasets). DUP: predicted exposure $\bar\pi\ge 0.01$; LOW: $0<\bar\pi<0.01$; CLEAN: no duplicated rows

| Task | Set | Datasets | Rows | Rows in duplicate groups | Predicted exposure $\bar\pi$ (median / max) | Datasets with label conflicts |
|---|---|---|---|---|---|---|
| Classification | DUP | 24 | 2,054 | 13.4% | 0.097 / 0.811 | 18 |
| Classification | LOW | 12 | 2,000 | 0.6% | 0.004 / 0.006 | 2 |
| Classification | CLEAN | 32 | 2,270 | 0.0% | 0.000 / 0.000 | 0 |
| Regression | DUP | 12 | 7,795 | 21.0% | 0.144 / 0.853 | 10 |
| Regression | LOW | 5 | 21,613 | 0.2% | 0.001 / 0.008 | 5 |
| Regression | CLEAN | 18 | 6,184 | 0.0% | 0.000 / 0.000 | 0 |

Proposition 2 predicts the exposure observed under random splitting almost exactly (Fig. 1b). The mean absolute error between predicted and observed exposure (the latter averaged over the 10 splits) is 0.0012, the maximum error is 0.021, and the Pearson correlation is 0.9998. A dataset's exposure can therefore be read off before any model is trained.

![**Fig. 1** (a) Analytic memorization limit of Proposition 1: novel-record coverage of split CP when seen records are always covered, as a function of exposure $\pi$ (dotted lines: nominal levels). (b) Exposure predicted by Proposition 2 from group sizes alone versus exposure observed under random 60/20/20 splits (mean over 10 splits); dashed line: identity](Fig1.png)

## Pre-specified test: is novel-record coverage below nominal across duplicated datasets?

Table 2 summarizes the primary analysis at $\alpha=0.1$. Averaged over datasets, standard split CP is close to nominal on novel records. Median gaps range from −0.8 to +2.6 percentage points (pp) across the 16 task × learner × score families, and **none of the one-sided tests of H1 is significant after Holm correction** (smallest adjusted $p$ = 0.092). The pre-specified primary hypothesis, that the *typical* duplicated benchmark dataset shows novel-record under-coverage, is therefore not supported.

The distribution of gaps is, however, strongly skewed. In every family the worst dataset under-covers novel records, by up to −6.9 pp in classification and −16.9 pp in regression. The share of DUP datasets that fall short by more than 1 pp ranges from 4–42% across families. As H1a predicts, the gap grows with exposure: Spearman correlations between exposure and gap range from −0.84 to −0.11, and they are negative and significant ($p<0.05$) in 10 of 16 families (Fig. 2). Overall coverage stays at nominal throughout (Online Resource 1, Table S3b), so the shortfall on novel records is invisible in the coverage that is normally reported.

The exception is $k$-NN with the LAC score, whose novel coverage is above nominal (median 0.926). A 5-NN classifier outputs class probabilities in multiples of 0.2, so its scores are heavily tied, which makes split CP conservative (see the null control below). The Friedman test across learners (H1b) is significant for LAC ($\chi^2$ = 51.6, $p$ < 0.001) and APS ($\chi^2$ = 16.6, $p$ = 0.002), but not for regression ($\chi^2$ = 4.3, $p$ = 0.363). For LAC the difference is driven by this tie effect rather than by memorization capacity. H1b is therefore better tested by the capacity experiment below, which varies flexibility within a learner.

**Table 2** Novel-record coverage gap (coverage − 0.90, in pp) under split CP with a random split (SCP-R) and novelty-Mondrian CP (MCP-R), on duplicated datasets (DUP), $\alpha=0.1$. Median over datasets [bootstrap 95% CI]; "Worst" is the minimum over datasets; $p_{\mathrm{H1}}$ and $p_{\mathrm{H2}}$ are Holm-adjusted one-sided Wilcoxon $p$-values; $\rho$ is the Spearman correlation between exposure and the SCP-R gap; "Size ratio" is the median ratio of MCP-R to SCP-R set size (or interval width) on novel records

| Task | Learner | Score | $n$ | SCP-R median gap | Worst | $p_{\mathrm{H1}}$ | $\rho$ | MCP-R median gap | $p_{\mathrm{H2}}$ | Size ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| Class. | LR | LAC | 24 | −0.46 [−1.05, +0.07] | −6.5 | 0.343 | −0.58 | +0.16 [−0.01, +0.56] | < 0.001 | 1.009 |
| Class. | LR | APS | 24 | −0.12 [−0.49, +0.22] | −1.5 | 1.000 | −0.64 | +0.19 [−0.12, +0.47] | 0.107 | 1.005 |
| Class. | RF | LAC | 24 | −0.64 [−1.53, +0.11] | −6.5 | 0.420 | −0.41 | +0.07 [−0.09, +0.32] | 0.107 | 1.012 |
| Class. | RF | APS | 24 | +0.52 [+0.02, +0.86] | −1.2 | 1.000 | −0.12 | +0.05 [−0.06, +0.65] | 0.979 | 0.995 |
| Class. | LightGBM | LAC | 24 | −0.64 [−1.27, −0.31] | −6.7 | 0.092 | −0.46 | +0.03 [−0.22, +0.34] | 0.005 | 1.011 |
| Class. | LightGBM | APS | 24 | −0.22 [−0.83, +0.18] | −4.2 | 0.607 | −0.84 | +0.19 [−0.18, +0.49] | 0.002 | 1.003 |
| Class. | k-NN | LAC | 24 | +2.59 [+0.87, +4.08] | −2.8 | 1.000 | −0.36 | +3.64 [+2.63, +4.46] | 0.061 | 1.000 |
| Class. | k-NN | APS | 24 | +0.09 [−0.31, +0.42] | −1.6 | 1.000 | −0.11 | +0.20 [−0.10, +0.54] | 0.229 | 1.001 |
| Class. | MLP | LAC | 24 | −0.44 [−0.85, +0.00] | −6.9 | 0.395 | −0.34 | +0.18 [−0.06, +0.52] | < 0.001 | 1.012 |
| Class. | MLP | APS | 24 | +0.02 [−0.60, +0.42] | −4.9 | 1.000 | −0.63 | +0.30 [+0.03, +0.60] | 0.002 | 1.005 |
| Regr. | LR | Abs. res. | 12 | −0.22 [−0.96, +0.03] | −16.8 | 1.000 | −0.80 | −0.00 [−0.49, +0.17] | 0.154 | 1.026 |
| Regr. | RF | Abs. res. | 12 | −0.81 [−1.41, +0.62] | −15.8 | 0.881 | −0.69 | +0.01 [−0.18, +0.49] | 0.107 | 1.043 |
| Regr. | LightGBM | Abs. res. | 12 | −0.62 [−1.75, +0.38] | −16.9 | 1.000 | −0.69 | −0.03 [−0.15, +0.97] | 0.061 | 1.027 |
| Regr. | k-NN | Abs. res. | 12 | −0.18 [−1.00, +0.41] | −11.7 | 1.000 | −0.37 | +0.04 [−0.35, +1.02] | 0.107 | 1.044 |
| Regr. | MLP | Abs. res. | 12 | −0.54 [−1.18, −0.01] | −10.8 | 0.833 | −0.62 | −0.05 [−0.37, +0.22] | 0.154 | 1.027 |
| Regr. | CQR | CQR | 12 | −0.64 [−1.83, +0.23] | −3.7 | 0.881 | −0.55 | +0.01 [−0.11, +0.90] | 0.011 | 1.017 |

![**Fig. 2** Novel-record coverage versus exposure for every duplicated dataset (mean over 10 splits, $\alpha=0.1$). Blue circles: split CP with a random split; orange diamonds: novelty-Mondrian CP; solid line: nominal level; dashed line: memorization limit $1-\alpha/(1-\pi)$](Fig2.png)

## Where the guarantee fails, and why (exploratory)

These analyses were added after the primary result and are labelled exploratory (Online Resource 1). Proposition 1 implies that exposure is necessary but not sufficient for a gap: seen records must also be over-covered. Table 3 stratifies the 312 dataset × learner × score combinations of the DUP set by exposure. Below $\pi=0.1$ (12 datasets), no combination falls short by more than 2 pp. For $0.1\le\pi<0.3$, 13% of combinations do, and for $\pi\ge 0.3$, 31% fall short by more than 2 pp and 19% by more than 5 pp. In total, 33 combinations from 12 datasets fall short by more than 2 pp, and 13 combinations from 4 datasets by more than 5 pp.

The decomposition of Proposition 1 shows which datasets fail (Fig. 3). The seen-coverage term $-\pi(c_{\mathrm S}-(1-\alpha))/(1-\pi)$ is strongly associated with the observed gap (Spearman $\rho$ = 0.55, against $\rho$ = −0.44 for exposure alone). The remaining marginal term is small (median absolute value 0.5 pp). The two most exposed datasets illustrate the point. In *solar_flare* ($\pi\approx 0.85$), seen records are covered at 0.92–0.94 and novel coverage falls to 0.73–0.79 across learners. In *cps88wages*, which has the same exposure but conflicting labels in almost every duplicate group, seen records are covered at the nominal rate (0.90) and novel records do not fall short (0.89–0.91). Large gaps also occur where duplicates mostly carry consistent labels, as in the NASA defect data (*kc1*: seen 0.97–0.98, novel 0.83–0.87), *breast-w* and the *Internet-Advertisements* data.

**Table 3** Exploratory: novel-record coverage gap (pp) by exposure stratum, pooled over learners, $\alpha=0.1$. $n_{\mathrm{ds}}$: datasets; $n$: dataset × learner combinations; P10: 10th percentile; "< −2 pp": share of combinations with a gap below −2 pp

| Exposure | Score | $n_{\mathrm{ds}}$ | $n$ | SCP-R median | SCP-R P10 | SCP-R worst | < −2 pp (%) | MCP-R median | MCP-R worst |
|---|---|---|---|---|---|---|---|---|---|
| π<0.1 | Abs. res. | 5 | 25 | −0.00 | −0.5 | −0.9 | 0 | +0.17 | −0.5 |
| π<0.1 | APS | 12 | 60 | +0.23 | −0.4 | −0.9 | 0 | +0.33 | −1.3 |
| π<0.1 | CQR | 5 | 5 | +0.18 | −0.4 | −0.4 | 0 | +0.62 | −0.4 |
| π<0.1 | LAC | 12 | 60 | +0.12 | −1.0 | −1.5 | 0 | +0.20 | −1.9 |
| 0.1≤π<0.3 | Abs. res. | 4 | 20 | −0.90 | −2.2 | −3.1 | 15 | −0.07 | −0.6 |
| 0.1≤π<0.3 | APS | 7 | 35 | −0.17 | −1.2 | −3.8 | 3 | −0.01 | −1.4 |
| 0.1≤π<0.3 | CQR | 4 | 4 | −1.53 | −2.2 | −2.2 | 25 | −0.11 | −0.2 |
| 0.1≤π<0.3 | LAC | 7 | 35 | −0.53 | −2.8 | −4.4 | 20 | +0.06 | −1.1 |
| π≥0.3 | Abs. res. | 3 | 15 | −1.28 | −16.4 | −16.9 | 33 | −0.17 | −5.8 |
| π≥0.3 | APS | 5 | 25 | −0.74 | −3.1 | −4.9 | 16 | +0.64 | −1.9 |
| π≥0.3 | CQR | 3 | 3 | −1.72 | −3.3 | −3.7 | 33 | −0.02 | −0.1 |
| π≥0.3 | LAC | 5 | 25 | −0.63 | −6.5 | −6.9 | 44 | +1.17 | −0.7 |

![**Fig. 3** Exploratory. (a) Observed novel-record gap of split CP versus the seen-coverage term of Proposition 1 for every duplicated dataset × learner × score (dashed line: identity; vertical deviations equal the marginal term). (b) Coverage of seen test records versus exposure; values are noisy where few test rows are seen](Fig3.png)

## External validation on data with documented duplication

The two curated suites contain few highly exposed datasets, and CTR23 excludes datasets that require grouped splits. After the first review round we therefore specified an external set before any outcome on it was computed (Online Resource 1, Table S2): every NASA MDP software-defect dataset on OpenML that is not in CC18 and has at least 300 rows, plus the 10% KDD Cup'99 intrusion data, whose redundancy is well documented (Tavallaee et al. 2009). The analysis used the same configuration as the main grid. Four of the 5 datasets have high exposure and almost no conflicting labels (Table 5).

In these data the shortfall is large and consistent. Of the 25 dataset × learner combinations (LAC score, $\alpha=0.1$), split CP under-covers novel records with a seed-level 95% confidence interval entirely below zero in 11, and entirely below −2 pp in 9. The worst mean gap is −27.5 pp. Novelty-Mondrian CP restores at least nominal coverage on novel records: its worst mean gap is −2.1 pp, and none of its confidence intervals lies entirely below zero. On KDD Cup'99, both methods over-cover with several learners (overall coverage up to 0.99). The thousands of identical calibration rows produce tied scores, which, as noted in the theory, preserve the lower coverage bound but not the upper one. In the suite datasets with $\bar\pi\ge 0.3$, seed-level intervals for split CP lie entirely below zero in 20 of 45 combinations (13 below −2 pp), and for novelty-Mondrian CP in 1.

**Table 5** External validation (classification, LAC, $\alpha=0.1$): novel-record coverage gap of split CP (pp; mean over 10 splits [seed-level 95% CI]) and range of the novelty-Mondrian CP gap across learners. "Rows" is the original size; KDD Cup'99 was uniformly subsampled to 30,000 rows, on which the duplicate share and $\bar\pi$ are computed

| Dataset | Rows | Rows in duplicate groups | $\bar\pi$ | LR | RF | LightGBM | k-NN | MLP | MCP-R range |
|---|---|---|---|---|---|---|---|---|---|
| mc1 | 9,466 | 84% | 0.82 | −17.5 [−19.5, −15.5] | −27.3 [−30.2, −24.4] | −19.9 [−23.1, −16.6] | +3.0 [+2.1, +3.9] | −16.9 [−21.3, −12.6] | −0.6 to +3.0 |
| kc3 | 458 | 38% | 0.33 | +0.8 [−1.9, +3.5] | −0.2 [−3.6, +3.2] | −0.7 [−3.7, +2.4] | +0.9 [−2.0, +3.9] | −0.7 [−4.8, +3.5] | +3.4 to +5.3 |
| pc2 | 5,589 | 83% | 0.81 | −25.5 [−28.2, −22.8] | −27.5 [−31.5, −23.4] | −17.2 [−22.1, −12.3] | +2.1 [+1.1, +3.2] | −3.1 [−5.7, −0.5] | −0.6 to +2.9 |
| mw1 | 403 | 10% | 0.07 | −2.9 [−6.0, +0.2] | −0.4 [−3.1, +2.2] | +0.1 [−2.0, +2.1] | +0.4 [−1.6, +2.3] | −0.6 [−2.7, +1.6] | −2.1 to +1.6 |
| KDDCup99 | 494,020 | 63% | 0.61 | −13.7 [−14.6, −12.7] | −1.4 [−1.9, −0.8] | +5.9 [+2.9, +8.8] | +8.5 [+8.3, +8.7] | −12.4 [−13.7, −11.1] | −0.4 to +8.5 |

## Controlled experiments

**Duplicate injection (dose–response).** Injecting exact copies into the duplicate-free datasets with at least 1,000 rows (21 classification, 16 regression) raised the exposure as Proposition 2 predicts. At duplication rates $\rho$ = 0.1, 0.25, 0.5 and 1, median exposure was 0.108, 0.241, 0.405 and 0.597. The novel-record gap of split CP grew monotonically for the flexible learners (Fig. 4). For random forests, the median gap went from +0.1 pp at $\rho=0$ to −6.1 pp at $\rho=0.5$ and −12.8 pp at $\rho=1$ in classification (−11.8 pp in regression), against a memorization limit of −14.8 pp. For LightGBM it reached −7.9 pp (classification) and −5.3 pp (regression). Regularized linear models were barely affected (−0.8 and −0.1 pp), because their seen records are not over-covered. The within-dataset Spearman correlation between $\rho$ and the gap was negative for RF (median −1.00, $p$ < 0.001; regression −1.00, $p$ < 0.001) and for LightGBM (median −1.00, $p$ < 0.001; regression −1.00, $p$ < 0.001). Novelty-Mondrian CP stayed at nominal at every rate (RF at $\rho=1$: +0.3 and +0.5 pp). For $k$-NN classification, tied scores make split CP conservative at baseline (+4.7 pp), and injection erodes this margin (+1.5 pp at $\rho=1$).

![**Fig. 4** Controlled duplicate injection into duplicate-free datasets: median novel-record coverage gap (coverage − 0.90) versus injected duplication rate, for split CP (solid) and novelty-Mondrian CP (dotted)](Fig4.png)

**Model capacity.** On the benchmark datasets with $\bar\pi\ge 0.05$ (20 classification, 9 regression), reducing flexibility lowered the coverage of seen records, as expected. For random forests the median went from 0.967 (leaf size 1) to 0.930 (leaf size 100) in classification, and from 0.972 to 0.921 in regression. The corresponding change in the novel-record gap was too small to detect, however. Median gaps were −0.7 versus −0.7 pp (classification) and −1.3 versus −0.6 pp (regression), and the within-dataset trend tests were not significant (RF: $p$ = 0.948 and 0.814; linear: $p$ = 0.851 and 0.934). At the moderate exposures of these datasets (median about 0.12–0.20), Proposition 1 predicts differences below 1 pp. The capacity half of H5 is therefore **not supported** by this experiment. The learner differences in the injection experiment, where flexible ensembles were affected far more than regularized linear models, are the stronger evidence for the role of capacity. For $k$-NN the experiment is uninformative: with $k=1$ the predicted probabilities are 0 or 1, the scores are almost all tied, and split CP returns near-trivial sets (median gap +10.0 pp). Fig. 5 shows the results.

![**Fig. 5** Capacity experiment on benchmark datasets with predicted exposure ≥ 0.05: median novel-record coverage gap versus capacity level (0 = most flexible), for split CP (solid) and novelty-Mondrian CP (dotted)](Fig5.png)

## Remedies

**Novelty-Mondrian CP (H2, H3).** MCP-R restores nominal coverage on novel records. Its median gap ranges from −0.1 to +0.3 pp across families (+3.6 pp for the tie-inflated $k$-NN/LAC combination), and the bootstrap confidence interval of the median lies above the −1 pp non-inferiority margin in all families (smallest lower bound −0.5 pp). It improves on SCP-R significantly after Holm correction in 6 of 16 families (Table 2). Its worst dataset-level gap is −5.8 pp, against −16.9 pp for SCP-R. That worst case (solar_flare) reflects sampling noise from only about 36 novel calibration rows per split: in a verification run with 200 further splits, MCP-R novel coverage was 0.909 (95% CI 0.899–0.918) for LightGBM and 0.907 (0.896–0.917) for ridge, while SCP-R reached 0.78 and 0.77. The trivial-set fallback was never triggered (0 dataset-level occurrences). The price is small. Median sets or intervals for novel records grow by a factor of 0.995–1.044, and the overall average changes by a factor of 0.987–1.009, because seen records receive tighter sets.

**Locally adaptive scores (additional baseline).** A natural question is whether a locally adaptive nonconformity score already absorbs the effect. Seen records lie at distance zero from their training copies, so a distance-normalized score gives them tighter intervals automatically. We therefore added, before computing its outcomes, the normalized residual $|y-\hat y|/(\hat\sigma(x)+\beta)$ of Papadopoulos et al. (2011) on the 12 duplicated regression datasets. Here $\hat\sigma(x)$ is the mean distance to the 10 nearest training rows and $\beta$ the median of $\hat\sigma$ over calibration rows. With this score, split CP was close to nominal on novel records. Median gaps were +0.1 pp (RF) and −0.1 pp (LightGBM), and the worst gaps were −3.4 and −2.6 pp, against −15.8 and −16.9 pp with the absolute residual. Only 1 dataset per learner remained more than 2 pp short. Adding novelty-Mondrian calibration on top of the normalized score brought no further systematic improvement (one-sided Wilcoxon $p$ = 0.545 and 0.551). Its worst values (−3.6 and −5.0 pp, both on solar_flare) again reflect the small novel calibration sets. In regression, a distance-adaptive score is therefore an effective heuristic mitigation. Unlike novelty-Mondrian calibration, however, it carries no group-conditional guarantee, and a residual shortfall of up to −3.4 pp remained. For classification, no comparably standard distance-normalized score exists; the six-bin distance-Mondrian variant (below) plays this role.

**Computational cost.** On 30,000-row datasets, hashing the records took at most 0.16 s, the audit at most 8 ms and the seen/novel taxonomy at most 7 ms. Computing the conformal thresholds took a median of 14 µs for split CP and 44 µs for novelty-Mondrian CP. Fitting and predicting with a single LightGBM model took 0.6–2.8 s (Online Resource 1). The remedy is therefore free in practice.

**Group-aware splitting (H6).** When whole record groups are assigned to one partition, every test row is novel by construction, and split CP attains median coverage 0.898–0.905 (excluding the tie-inflated $k$-NN/LAC combination). Non-inferiority at −1 pp holds in all families (Online Resource 1). Group splitting answers a different question, however. It estimates coverage for new records only, and it changes the training set. Novelty-Mondrian CP keeps the standard split and is valid for any mix of seen and new records (Corollary 1).

**Null control.** On the duplicate-free datasets, split CP is at nominal coverage (median 0.899–0.902; $k$-NN/LAC 0.941 because of tied scores), and MCP-R is identical to SCP-R (largest absolute difference 0), as it must be when no row is seen.

**Secondary miscoverage levels.** At $\alpha=0.05$ the median SCP-R gaps range from −0.4 to +2.0 pp (worst −10.6 pp; families significant after Holm correction: 1). At $\alpha=0.2$ they range from −1.6 to +3.9 pp (worst −25.8 pp; significant: 1). The smallest lower confidence bound of the MCP-R median gap is −0.4 pp and −0.5 pp, respectively.

## Calibration of predicted probabilities (H4)

Classifiers are markedly more accurate on seen than on novel test records (median accuracy 0.938–0.985 versus 0.852–0.918 across learners; Table 4). Overconfidence on novel records exceeds overconfidence on all records in 3 of 5 learners after Holm correction. Novel-record ECE exceeds size-matched ECE in 3 of 5. The median differences are small, however (−0.29 to +0.43 pp for overconfidence and +0.04 to +0.33 pp for ECE). H4 is supported statistically but with small effect sizes: the large accuracy gap between seen and novel records is largely matched by lower confidence on novel records (Fig. 6).

**Table 4** Calibration on the duplicated classification datasets (random split; medians over datasets). OC: overconfidence (mean confidence − accuracy, pp); ECE in %; $p$: Holm-adjusted one-sided Wilcoxon tests of novel versus all rows (OC) and novel versus size-matched subsets (ECE)

| Learner | $n$ | Acc. seen | Acc. novel | OC all | OC novel | $p_{\mathrm{OC}}$ | ECE size-matched | ECE novel | $p_{\mathrm{ECE}}$ |
|---|---|---|---|---|---|---|---|---|---|
| LR | 24 | 0.938 | 0.910 | +0.22 | +0.45 | 0.021 | 3.56 | 3.87 | 0.036 |
| RF | 24 | 0.985 | 0.918 | −0.79 | −0.95 | 0.997 | 4.68 | 5.66 | 0.060 |
| LightGBM | 24 | 0.981 | 0.909 | +4.54 | +5.80 | 0.002 | 5.54 | 7.05 | 0.003 |
| k-NN | 24 | 0.954 | 0.852 | +1.72 | +1.96 | 0.056 | 5.59 | 6.11 | 0.036 |
| MLP | 24 | 0.957 | 0.910 | −1.39 | −1.00 | 0.021 | 6.13 | 5.91 | 0.322 |

![**Fig. 6** Overconfidence (mean top-label confidence − accuracy) on seen, all and novel test rows for each duplicated classification dataset (dots) and learner; black bars: medians](Fig6.png)

## Near-duplicates (exploratory)

Coverage of split CP also varies with the distance of a novel record to its nearest training record (Fig. 7). For novel records in the nearest distance quintile, median coverage is 0.945 (classification, LAC) and 0.940 (regression). In the farthest quintile it is 0.876 and 0.837. Seen records are covered at 0.975 and 0.941. A six-bin Mondrian variant built on the same training-only distance bins keeps every bin's median coverage at or above 0.907 (classification) and 0.901 (regression). Exact duplication is therefore the extreme case of a more general dependence of coverage on novelty, which difficulty-based Mondrian calibration (Boström and Johansson 2020) addresses.

![**Fig. 7** Exploratory. Median coverage of split CP by distance of the test record to its nearest training record (quintile bins with training-only edges; "Seen" = exact training copy), and of the six-bin distance-Mondrian variant (dotted), $\alpha=0.1$](Fig7.png)


# Discussion

## What the evidence establishes

Under a random row split, the marginal guarantee of split CP is honoured on average (overall coverage was at nominal throughout), but it can conceal a shortfall on records the model has not seen. Proposition 1 states exactly when this happens: novel records are under-covered by the amount by which seen records are over-covered, scaled by $\pi/(1-\pi)$. The empirical results follow that mechanism. The shortfall grew with exposure in the benchmark data, it appeared as a dose–response when duplicates were injected into clean data, and it disappeared on datasets where duplicate groups carry conflicting labels, because there the model cannot over-cover its seen records. The role of model flexibility is supported only partly. In the injection experiment flexible ensembles were affected far more than regularized linear models, but varying regularization within a learner at the moderate exposures of the benchmark data produced no detectable change in the gap, although seen-record coverage fell as expected. Novelty-Mondrian calibration restored nominal coverage on novel records in every family, with set-size increases of a few percent, and it did nothing on duplicate-free data, as it should. A distance-normalized regression score also removed most of the shortfall, which shows that the problem is specific to scores that ignore how close a test record is to the training data.

The pre-specified primary hypothesis was nonetheless not supported. Across the duplicated datasets of two standard suites, the *median* gap is a fraction of a percentage point. For most benchmark datasets used in CP research, duplicate leakage therefore does not materially distort reported coverage, and this negative result is itself useful. The practical risk lies in the tail: datasets with high exposure and consistent duplicate labels. There, novel-record coverage was up to −16.9 points below what is reported in the benchmark suites (solar_flare). In the external NASA defect and KDD Cup'99 data, whose duplication problems are documented (Gray et al. 2011; Shepperd et al. 2013; Tavallaee et al. 2009), it was up to −27.5 points below.

In natural data, seen and novel records also differ in typicality: frequently repeated profiles are common configurations, whereas novel records are often rare ones. Part of the observed gap may therefore reflect that novel records are intrinsically harder, not only that the model memorized its training rows. The injection experiment separates the two. There, duplicated rows were chosen uniformly at random, so seen and novel records come from the same distribution, and the gap still grew with exposure for flexible learners.

## Recommendations

1. **Audit before evaluating.** Count duplicate groups and compute the expected exposure (Proposition 2). It is label-free, takes seconds, and predicted observed exposure almost exactly.
2. **Report coverage separately for seen and novel test rows** whenever exposure is not negligible (in our data, $\bar\pi\ge 0.1$ was the regime with material shortfalls). Over-coverage of seen rows is the warning sign.
3. **Prefer distance-adaptive scores, and use novelty-Mondrian calibration when a guarantee is needed.** In our regression data, a nonconformity score normalized by nearest-neighbour distance removed most of the shortfall without any seen/novel split. It is a heuristic, though, and it left residual gaps of a few points. Novelty-Mondrian calibration is the option with a finite-sample guarantee.
4. **Choose the estimand deliberately.** If deployment involves new entities, use novelty-Mondrian calibration, which keeps the standard split and is valid for any mix of seen and new records, or a group-aware split, which evaluates new records only. If identical profiles legitimately recur at deployment, the row-level guarantee may be the right target, but the seen/novel breakdown should still be reported.

## Relation to prior work

Our findings complement the duplicate audits of Li (2026) and Roth (2026). They show inflated accuracy and distorted rankings; we show that the formal coverage guarantee of CP is affected in a predictable, quantifiable way, and that a remedy with a guarantee exists. Group-conditional CP has been used for protected groups (Romano et al. 2020b), classes (Löfström et al. 2015; Ding et al. 2023) and difficulty strata (Boström and Johansson 2020). The grouping studied here differs in two ways: it is induced by the split itself, and it is defined by membership of the training set. Lemma 0 shows that conditioning on the training set makes such a data-dependent taxonomy admissible. The near-duplicate analysis indicates that exact duplication is the extreme case of a broader dependence of coverage on distance to the training data, consistent with work on localized and difficulty-adaptive CP (Papadopoulos et al. 2011; Guan 2023).

## Limitations

* **Scope of data.** The study uses two curated OpenML suites (103 datasets after excluding four image datasets) with fixed default hyperparameters. Other domains, such as logs, electronic health records or intrusion-detection data, may contain far more duplication. Tuned models may memorize more or less than our defaults; the capacity experiment brackets this, but not exhaustively.
* **Exact duplicates only.** Records duplicated with small perturbations are counted as novel, so measured exposure is a lower bound. The near-duplicate analysis is exploratory.
* **Few high-exposure datasets.** Only 9 benchmark datasets have exposure of at least 0.3. The large gaps rest on a small number of datasets, which is why the controlled injection experiment was used to establish the dose–response causally.
* **Variability with small novel calibration sets.** Novelty-Mondrian CP is valid in expectation, but when few novel calibration rows exist, its coverage varies considerably from split to split (per-split SD ≈ 0.07 with about 36 rows on solar_flare). Training-conditional (PAC-type) guarantees would require larger calibration sets.
* **Estimand assumption.** Whether new deployment records behave like novel held-out rows is an assumption about the data-generating process, not something the theory or the benchmark data can establish.
* **Capacity hypothesis.** The within-learner capacity experiment was underpowered for the small gap differences that the theory predicts at moderate exposure, and for $k$-NN it was dominated by tied scores. The capacity hypothesis was therefore not confirmed.
* **Post hoc analyses.** The exposure-stratified and decomposition analyses were added after the primary result and are exploratory. The external validation set was specified after the first internal review round, but before its outcomes were computed.
* **Protocol registration.** The protocol was fixed by a version-control commit, not by an external registry, so readers must rely on the repository history to verify its timing.


# Conclusion

Duplicate records do not invalidate the marginal guarantee of conformal prediction, but they can redistribute its errors onto new records. The size of that shift is given exactly by the exposure and the over-coverage of seen records. In standard tabular benchmarks the shift is negligible for most datasets but substantial for a predictable minority. A label-free audit identifies the minority. Distance-adaptive scores mitigate the problem, and novelty-Mondrian calibration repairs coverage on new records with a finite-sample guarantee at small cost. We recommend that conformal evaluations on tabular data report duplicate exposure and coverage on novel records alongside the usual marginal coverage.


# Statements and Declarations {-}

**Competing interests.** [AUTHOR TO CONFIRM: The authors declare that they have no known competing financial or non-financial interests.]

**Funding.** [AUTHOR TO CONFIRM: No funding was received for conducting this study.]

**Author contributions.** [AUTHOR TO COMPLETE, e.g. in CRediT format, after the author list is fixed.]

**Ethics approval and consent to participate.** Not applicable. The study uses only publicly available, de-identified benchmark datasets from OpenML and involves no human participants or animals.

**Data availability.** All datasets are public and are identified by their OpenML dataset identifiers in Online Resource 1 (OpenML suites 99 and 353). All raw per-split results, aggregated tables and statistics supporting the findings are included in the code repository.

**Code availability.** The complete pipeline (audit, experiments, statistics, figures, manuscript build) is available as a version-controlled repository. A single command reproduces every reported number. [AUTHOR TO COMPLETE: archive the repository with a DOI (e.g. Zenodo), insert the link, and provide an anonymized copy for double-anonymous review.]

**Use of AI tools.** The study design, literature search, code, experiments, statistical analysis and drafting of this manuscript were carried out with substantial assistance from an AI system (a large language model operating as an agent with code-execution tools), under the direction of the human author(s). All numerical results were produced by executed code whose outputs are archived with the repository. The human author(s) reviewed the work and take full responsibility for its content. [AUTHOR TO CONFIRM wording against the journal's current AI policy.]


# References {-}

Allamanis M (2019) The adverse effects of code duplication in machine learning models of code. In: Proceedings of the 2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software (Onward! 2019), pp 143–153. https://doi.org/10.1145/3359591.3359735

Angelopoulos AN, Bates S (2023) Conformal prediction: a gentle introduction. Found Trends Mach Learn 16(4):494–591. https://doi.org/10.1561/2200000101

Barber RF, Candès EJ, Ramdas A, Tibshirani RJ (2023) Conformal prediction beyond exchangeability. Ann Stat 51(2):816–845. https://doi.org/10.1214/23-AOS2276

Barz B, Denzler J (2020) Do we train on test data? Purging CIFAR of near-duplicates. J Imaging 6(6):41. https://doi.org/10.3390/jimaging6060041

Bastani O, Gupta V, Jung C, Noarov G, Ramalingam R, Roth A (2022) Practical adversarial multivalid conformal prediction. In: Advances in Neural Information Processing Systems 35, pp 29362–29373. https://doi.org/10.52202/068431-2129

Bischl B, Casalicchio G, Feurer M, Gijsbers P, Hutter F, Lang M, Mantovani RG, van Rijn JN, Vanschoren J (2021) OpenML benchmarking suites. In: Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks 1. arXiv:1708.03731

Boström H, Johansson U (2020) Mondrian conformal regressors. In: Proceedings of the Ninth Symposium on Conformal and Probabilistic Prediction and Applications, PMLR 128:114–133

Breiman L (2001) Random forests. Mach Learn 45(1):5–32. https://doi.org/10.1023/A:1010933404324

Ding T, Angelopoulos AN, Bates S, Jordan MI, Tibshirani RJ (2023) Class-conditional conformal prediction with many classes. In: Advances in Neural Information Processing Systems 36. arXiv:2306.09335

Dunn R, Wasserman L, Ramdas A (2023) Distribution-free prediction sets for two-layer hierarchical models. J Am Stat Assoc 118(544):2491–2502. https://doi.org/10.1080/01621459.2022.2060112

Elangovan A, He J, Verspoor K (2021) Memorization vs. generalization: quantifying data leakage in NLP performance evaluation. In: Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics, pp 1325–1335. https://doi.org/10.18653/v1/2021.eacl-main.113

Fischer SF, Feurer M, Bischl B (2023) OpenML-CTR23 – a curated tabular regression benchmarking suite. In: AutoML Conference 2023 (Workshop Track). OpenML study 353

Foygel Barber R, Candès EJ, Ramdas A, Tibshirani RJ (2021) The limits of distribution-free conditional predictive inference. Inf Inference 10(2):455–482. https://doi.org/10.1093/imaiai/iaaa017

Friedman M (1937) The use of ranks to avoid the assumption of normality implicit in the analysis of variance. J Am Stat Assoc 32(200):675–701. https://doi.org/10.1080/01621459.1937.10503522

Gibbs I, Cherian JJ, Candès EJ (2025) Conformal prediction with conditional guarantees. J R Stat Soc Ser B Stat Methodol 87(4):1100–1126. https://doi.org/10.1093/jrsssb/qkaf008

Gray D, Bowes D, Davey N, Sun Y, Christianson B (2011) The misuse of the NASA metrics data program data sets for automated software defect prediction. In: 15th Annual Conference on Evaluation & Assessment in Software Engineering (EASE 2011), pp 96–103. https://doi.org/10.1049/ic.2011.0012

Guan L (2023) Localized conformal prediction: a generalized inference framework for conformal prediction. Biometrika 110(1):33–50. https://doi.org/10.1093/biomet/asac040

Guo C, Pleiss G, Sun Y, Weinberger KQ (2017) On calibration of modern neural networks. In: Proceedings of the 34th International Conference on Machine Learning, PMLR 70:1321–1330

Hernandez-Hernandez S, Guo Q, Ballester PJ (2026) Conformal prediction of molecule-induced cancer cell growth inhibition challenged by strong distribution shifts. Pattern Recognit 172:112501. https://doi.org/10.1016/j.patcog.2025.112501

Holm S (1979) A simple sequentially rejective multiple test procedure. Scand J Stat 6(2):65–70

Kapoor S, Narayanan A (2023) Leakage and the reproducibility crisis in machine-learning-based science. Patterns 4(9):100804. https://doi.org/10.1016/j.patter.2023.100804

Kaufman S, Rosset S, Perlich C, Stitelman O (2012) Leakage in data mining. ACM Trans Knowl Discov Data 6(4):1–21. https://doi.org/10.1145/2382577.2382579

Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, Ye Q, Liu TY (2017) LightGBM: a highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30, pp 3146–3154

Lee K, Ippolito D, Nystrom A, Zhang C, Eck D, Callison-Burch C, Carlini N (2022) Deduplicating training data makes language models better. In: Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics, pp 8424–8445. https://doi.org/10.18653/v1/2022.acl-long.577

Lei J, G'Sell M, Rinaldo A, Tibshirani RJ, Wasserman L (2018) Distribution-free predictive inference for regression. J Am Stat Assoc 113(523):1094–1111. https://doi.org/10.1080/01621459.2017.1307116

Lewis P, Stenetorp P, Riedel S (2021) Question and answer test-train overlap in open-domain question answering datasets. In: Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics, pp 1000–1008. https://doi.org/10.18653/v1/2021.eacl-main.86

Li H (2026) Rows are not samples: duplicate records, evaluation bias, and ranking distortion in standard tabular benchmarks. Zenodo (preprint, not peer reviewed). https://doi.org/10.5281/zenodo.23119065

Löfström T, Boström H, Linusson H, Johansson U (2015) Bias reduction through conditional conformal prediction. Intell Data Anal 19(6):1355–1375. https://doi.org/10.3233/IDA-150786

Morger A, Svensson F, Arvidsson McShane S, Gauraha N, Norinder U, Spjuth O, Volkamer A (2021) Assessing the calibration in toxicological in vitro models with conformal prediction. J Cheminform 13:35. https://doi.org/10.1186/s13321-021-00511-5

Naeini MP, Cooper G, Hauskrecht M (2015) Obtaining well calibrated probabilities using Bayesian binning. Proc AAAI Conf Artif Intell 29(1). https://doi.org/10.1609/aaai.v29i1.9602

Norinder U, Carlsson L, Boyer S, Eklund M (2014) Introducing conformal prediction in predictive modeling. A transparent and flexible alternative to applicability domain determination. J Chem Inf Model 54(6):1596–1603. https://doi.org/10.1021/ci5001168

Papadopoulos H, Proedrou K, Vovk V, Gammerman A (2002) Inductive confidence machines for regression. In: Machine Learning: ECML 2002. Lecture Notes in Computer Science, vol 2430, pp 345–356. https://doi.org/10.1007/3-540-36755-1_29

Papadopoulos H, Vovk V, Gammerman A (2011) Regression conformal prediction with nearest neighbours. J Artif Intell Res 40:815–840. https://doi.org/10.1613/jair.3198

Pedregosa F, Varoquaux G, Gramfort A, et al (2011) Scikit-learn: machine learning in Python. J Mach Learn Res 12:2825–2830

Romano Y, Barber RF, Sabatti C, Candès EJ (2020b) With malice toward none: assessing uncertainty via equalized coverage. Harv Data Sci Rev. https://doi.org/10.1162/99608f92.03f00592

Romano Y, Patterson E, Candès EJ (2019) Conformalized quantile regression. In: Advances in Neural Information Processing Systems 32. arXiv:1905.03222

Romano Y, Sesia M, Candès EJ (2020a) Classification with valid and adaptive coverage. In: Advances in Neural Information Processing Systems 33. arXiv:2006.02544

Roth S (2026) Which leakage types matter? A quantitative landscape across 2,047 benchmark datasets. arXiv:2604.04199 (preprint, not peer reviewed)

Sadinle M, Lei J, Wasserman L (2019) Least ambiguous set-valued classifiers with bounded error levels. J Am Stat Assoc 114(525):223–234. https://doi.org/10.1080/01621459.2017.1395341

Seo J-I, Jeon YE, Kim Y (2026) Calibrated Mondrian conformal prediction for uncertainty quantification in spatial modeling. Pattern Recognit 180:114113. https://doi.org/10.1016/j.patcog.2026.114113

Shepperd M, Song Q, Sun Z, Mair C (2013) Data quality: some comments on the NASA software defect datasets. IEEE Trans Softw Eng 39(9):1208–1215. https://doi.org/10.1109/TSE.2013.11

Sheridan RP (2013) Time-split cross-validation as a method for estimating the goodness of prospective prediction. J Chem Inf Model 53(4):783–790. https://doi.org/10.1021/ci400084k

Tavallaee M, Bagheri E, Lu W, Ghorbani AA (2009) A detailed analysis of the KDD CUP 99 data set. In: 2009 IEEE Symposium on Computational Intelligence for Security and Defense Applications, pp 1–6. https://doi.org/10.1109/CISDA.2009.5356528

Tibshirani RJ, Barber RF, Candès EJ, Ramdas A (2019) Conformal prediction under covariate shift. In: Advances in Neural Information Processing Systems 32. arXiv:1904.06019

Vanschoren J, van Rijn JN, Bischl B, Torgo L (2014) OpenML: networked science in machine learning. SIGKDD Explor 15(2):49–60. https://doi.org/10.1145/2641190.2641198

Vovk V (2012) Conditional validity of inductive conformal predictors. In: Proceedings of the Asian Conference on Machine Learning, PMLR 25:475–490

Vovk V, Gammerman A, Shafer G (2022) Algorithmic learning in a random world, 2nd edn. Springer, Cham. https://doi.org/10.1007/978-3-031-06649-8

Wilcoxon F (1945) Individual comparisons by ranking methods. Biometrics Bull 1(6):80–83. https://doi.org/10.2307/3001968


Zhang R, Zhou P (2026) A Mondrian conformal predictive system with improved decision trees for uncertainty quantification under heteroscedasticity. Pattern Recognit 172:112338. https://doi.org/10.1016/j.patcog.2025.112338
