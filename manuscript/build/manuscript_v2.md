---
title: "Duplicate Data Rows Make Prediction Uncertainty Look Better Than It Is: A Simple Check and Fix for New Cases"
---

**Abstract** Conformal prediction wraps a machine-learning model so that its prediction sets contain the true answer at a promised rate, for example 90% of the time. Practitioners usually confirm this promise on a random test split. Tabular data, however, often contain repeated rows, and a random split then places copies of many test rows in the training data. The check averages over these easy repeats and genuinely new cases, so it can report 90% while new cases, the ones that matter after deployment, are covered far less often. We propose a three-step routine: check, fix, report. The check counts repeated rows and whether they agree on the label, and predicts the worst-case shortfall before any model is trained. The fix calibrates seen and new cases separately, which restores the promised coverage for new cases. The report states coverage on new cases next to the usual figure. In software-defect prediction, a random forest's sets reported 91.7% coverage but covered only 62.7% of new modules; after the fix, 90.3%. Similar shortfalls appeared in phishing and network-intrusion data. Across 103 benchmark data sets the problem was usually small, and the check said so. On 20 fresh data sets analysed under a plan fixed in advance, the fix kept new-case coverage on target and the check separated safe from risky data, although it did not rank data sets by severity. The routine takes seconds and needs no change to the model.

**Keywords** Conformal prediction · Uncertainty quantification · Duplicate records · Data leakage · Software defect prediction · Tabular data


# Introduction

Suppose a software quality team uses a classifier to flag modules that are likely to contain defects. A bare yes/no answer is not enough for planning reviews, so the team wraps the classifier in conformal prediction. For each module it now gets a small set of possible labels that is promised to contain the true one 90% of the time (Vovk et al. 2022; Angelopoulos and Bates 2023). Before trusting the promise, the team checks it the usual way: it splits its historical data at random into training, calibration and test parts and counts how often the sets were right. The answer is close to 90%, and the system goes into use.

What the team may not have noticed is that its historical data contain many repeated rows. In NASA's public defect data, for example, a large share of modules have exactly the same metric values as other modules (Gray et al. 2011; Shepperd et al. 2013). Repeats like these are common in tabular data: the same network connection logged thousands of times, the same customer profile entered twice, identical sensor readings. A random split then places copies of many test rows in the training set. The model has effectively seen those answers, so its sets are almost always right for them. The 90% the team measured is an average over these easy repeats and the cases that are actually new. New modules, which are what the team will face after deployment, may be covered far less often.

This is not a hypothetical concern. On the NASA *mc1* data, a random forest's 90% sets were right for 91.7% of test rows, but only for 62.7% of genuinely new modules. Comparable shortfalls appear in phishing-website detection and network-intrusion data (Section 5). Duplicate rows are known to inflate accuracy figures (Kapoor and Narayanan 2023; Li 2026; Roth 2026). Their effect on the *uncertainty* estimates that practitioners rely on for risk decisions has received little attention, even though here a stated guarantee, not just an estimate, is what quietly fails.

This paper offers a practical answer in three steps, which we call *check, fix, report*.

* **Check.** Before training anything, count the repeated rows and test whether repeats agree on the label. Two short formulas turn these counts into the share of test rows that will be seen and a predicted worst-case shortfall for new cases (Section 3).
* **Fix.** If the check signals risk, calibrate seen and new cases separately. This restores the promised coverage for new cases, for any mix of seen and new cases at deployment, and costs almost nothing to compute (Section 3.4).
* **Report.** State the coverage on new cases next to the usual overall figure.

We evaluate the procedure in three ways. First, on three real application areas: software-defect prediction, network-intrusion detection and phishing detection. Second, on 103 standard benchmark data sets together with controlled experiments in which we add exact or slightly perturbed copies to clean data. Third, on a fresh collection of data sets that we selected and analysed only after the procedure was fixed. The overall picture is reassuring for most benchmark data: the problem is small where the check says it is small. Where the check raises a flag, the shortfall is often real and sometimes large, and the fix removes it; where the flag turns out to be a false alarm, the fix costs almost nothing. All code and results are openly available.


# Background and related work

**Conformal prediction.** Split conformal prediction turns any fitted model into prediction sets or intervals with a coverage guarantee that holds in finite samples, provided calibration and test data are exchangeable (Papadopoulos et al. 2002; Lei et al. 2018; Vovk et al. 2022). It is increasingly used in applied work, for example in drug discovery and toxicology (Norinder et al. 2014; Morger et al. 2021; Hernandez-Hernandez et al. 2026). We use the standard nonconformity scores: $1-\hat p_y$ for classification (Sadinle et al. 2019), the adaptive APS score (Romano et al. 2020a), the absolute residual for regression and conformalized quantile regression (Romano et al. 2019). The guarantee is *marginal*, meaning it is averaged over all test cases. Coverage for every individual input cannot be guaranteed without further assumptions (Vovk 2012; Foygel Barber et al. 2021). Coverage within a fixed set of groups can be achieved, either by calibrating each group separately (Mondrian conformal prediction; Vovk et al. 2022) or by more general and localized conditional calibration (Guan 2023; Gibbs et al. 2025; Bastani et al. 2022). Group-wise calibration has been used for protected groups (Romano et al. 2020b), classes (Löfström et al. 2015; Ding et al. 2023), difficulty bins (Boström and Johansson 2020), two-level group structures (Dunn et al. 2023), predictive distributions (Zhang and Zhou 2026) and, recently, spatial regions (Seo et al. 2026) and demographic strata in clinical screening (Tareaf et al. 2026). Training-conditional guarantees, which hold with high probability over the calibration draw, go back to Vovk (2012). Our fix uses these standard tools. What is new is *which* groups need separate calibration, *why*, and how to tell in advance whether it matters.

**Repeated rows and leakage.** Information leaking from evaluation data into training is a well-known source of over-optimism (Kaufman et al. 2012; Kapoor and Narayanan 2023). Overlap between training and test data has been documented for images (Barz and Denzler 2020), text (Lee et al. 2022; Lewis et al. 2021; Elangovan et al. 2021) and source code (Allamanis 2019), and for tabular data in software-defect and intrusion-detection benchmarks (Gray et al. 2011; Shepperd et al. 2013; Tavallaee et al. 2009). Three recent preprints study repeated rows across many tabular data sets. Li (2026) shows that random splits inflate accuracy and can change which model looks best. Roth (2026) finds that this kind of leakage grows with model flexibility. Deng (2026) audits 690 anomaly-detection benchmarks and builds a detector whose false-alarm rate, calibrated with split conformal prediction, does not change when rows are replicated. These studies concern accuracy, ranking or unsupervised false-alarm control. None of them examines whether the coverage promised by conformal prediction sets holds for new cases in supervised prediction, or how to predict and repair a shortfall. That is the gap this paper addresses.


# Why repeated rows distort the check

## Setting and notation

A data set $D$ of $N$ rows is split at random into a training part $T$, a calibration part $C$ and a test part $E$ (60/20/20 in all our experiments). Rows with exactly the same feature values form a *record group*. A calibration or test row is *seen* if some training row has the same feature values, and *new* otherwise. The model is fitted on $T$ and produces a nonconformity score $s(x,y)$; split conformal prediction returns the set $\{y: s(x,y)\le\hat q\}$, where $\hat q$ is the $\lceil (n_C+1)(1-\alpha)\rceil$-th smallest calibration score (Lei et al. 2018). Throughout, $\alpha=0.1$, so the promise is 90% coverage.

Given the training part, the remaining rows are still assigned to calibration and test at random. This is all split conformal prediction needs: averaged over test rows, coverage is at least $1-\alpha$ (Vovk et al. 2022). The guarantee is about a random test **row**, and a random test row may well be a copy of a training row.

## The shortfall on new cases

Write $\pi$ for the share of test rows that are seen, $c$ for the overall coverage, and $c_S$ and $c_N$ for the coverage of seen and new rows. Because a test row is either seen or new,
$$c = \pi\,c_S + (1-\pi)\,c_N, \qquad\text{so}\qquad c_N = \frac{c-\pi c_S}{1-\pi}. \tag{1}$$
Since the method keeps $c$ close to $1-\alpha$, new cases are under-covered exactly when seen cases are over-covered. In the extreme case where every seen row is covered ($c_S=1$), the error rate on new cases becomes $\alpha/(1-\pi)$ instead of $\alpha$: with half of the test rows seen, one new case in five is missed while the check still reports 90%.

## The check: two numbers that can be computed before training

Equation (1) needs $c_S$, which requires a trained model. Two quantities that need only the data tell us in advance how large the problem can become.

*Exposure.* If a test row belongs to a group of $m$ identical rows and $n_T$ of the other $N-1$ rows go to training, the chance that none of its $m-1$ copies lands in training is $\binom{N-m}{n_T}/\binom{N-1}{n_T}$. Averaging over rows gives the expected share of seen test rows,
$$\bar\pi=\sum_g \frac{m_g}{N}\Big[1-\binom{N-m_g}{n_T}\Big/\binom{N-1}{n_T}\Big]. \tag{2}$$

*Label purity.* Exposure alone can mislead. If repeated rows disagree on the label (in survey or wage data, identical profiles often have different outcomes), memorizing them does not help the model, and seen rows are not over-covered. Let $\pi_P$ be the share of test rows whose training copies all carry exactly the test row's label (or, in regression, its target value). These are the rows a flexible model can simply look up. If those rows receive the lowest possible score and all other rows share one score distribution, the calibration threshold settles where $\pi_P+(1-\pi_P)F(\hat q)=1-\alpha$, so coverage of new cases tends to
$$c_N \to 1-\frac{\alpha}{1-\pi_P}, \qquad \text{a shortfall of } g^*=-\frac{\alpha\,\pi_P}{1-\pi_P}. \tag{3}$$
We call $g^*$ the *predicted shortfall* (or predicted gap). It is a worst case for models that memorize their training rows; less flexible models should fall short by less. It can fail when repeated rows disagree on the label but are still easy to predict, for example when their regression targets differ only slightly. We test both points below. A short derivation of Eqs. (1)–(3) and a simulation check are given in Appendix A.

## The fix: calibrate seen and new cases separately

The remedy is to compute two thresholds, one from seen calibration rows and one from new calibration rows, and to apply each to the matching test rows. This is Mondrian conformal prediction (Vovk et al. 2022) with the categories "seen" and "new". Because the categories are fixed once the training part is chosen, calibration and test rows within each category remain exchangeable, and the usual argument gives coverage of at least $1-\alpha$ **separately** for seen and for new cases (Appendix A). The promise therefore holds for any mix of the two, including a deployment where every case is new. If too few new calibration rows exist (fewer than $1/\alpha-1$), the method honestly returns the full set for new cases.

Two variants are useful in practice. The first adds a *safety margin*: with only a few dozen new calibration rows, coverage varies noticeably from one split to the next, and choosing a slightly higher rank gives coverage of at least $1-\alpha$ with probability $1-\delta$ over the calibration draw (Vovk 2012). The second, for regression, scales each residual by the average distance to the ten nearest training rows (Papadopoulos et al. 2011), which automatically gives tighter intervals to rows that sit on top of a training copy.


# How we evaluated the procedure

**Applications.** We use three applications where repeated records are known to occur. For *software-defect prediction*, we take all ten NASA Metrics Data Program sets available on OpenML with at least 300 modules: kc1, kc2, pc1, pc3, pc4 and jm1 (part of the OpenML-CC18 suite), and mc1, pc2, kc3 and mw1. For *network-intrusion detection*, we take the 10% KDD Cup'99 data (Tavallaee et al. 2009), randomly reduced to 30,000 connections. For *phishing detection*, we take the PhishingWebsites data from OpenML-CC18.

**Benchmarks.** To see how common the problem is, we analysed all 103 tabular data sets of two widely used OpenML suites: 68 classification sets from OpenML-CC18 (Bischl et al. 2021), excluding four image sets, and 35 regression sets from OpenML-CTR23 (Fischer et al. 2023). Data sets larger than 30,000 rows were reduced by sampling whole groups of identical rows, so that the repetition structure was kept.

**Controlled experiments.** To show that repetition itself causes the shortfall, we took the 37 benchmark sets that have no repeated rows and at least 1,000 rows, and appended copies of a random 10%, 25%, 50% or 100% of their rows. To see what happens when repeats are not exact, we repeated this with 50% copies whose numeric features were perturbed by small random noise (0.1%, 1% or 10% of each feature's standard deviation). In the perturbed setting the exact-match check cannot see the copies, so we measured coverage on rows whose *original record* never appeared in training.

**A fresh validation set.** The predicted-shortfall formula (3) was derived after we had seen the benchmark results. To test it fairly, we fixed the analysis plan in a time-stamped version-control commit and then collected new data sets from OpenML collections we had not used: the AutoML Benchmark (Gijsbers et al. 2024) and the tabular benchmark of Grinsztajn et al. (2022). Data sets were included if the check, which uses no labels and no models, predicted at least 1% seen test rows. Data sets with more than 30,000 rows were reduced as above, except that a uniform row sample was used when a single group of identical rows exceeded 6,000 rows (a rule also fixed in advance). We used 20 random splits per data set.

**Models and settings.** Five common learners were trained with fixed default settings: logistic or ridge regression, random forest (200 trees; Breiman 2001), LightGBM (300 trees; Ke et al. 2017), 5-nearest neighbours and a small neural network. The fresh validation set used the first three. Models were implemented with scikit-learn (Pedregosa et al. 2011) and LightGBM, and all data were obtained from OpenML (Vanschoren et al. 2014). All preprocessing was fitted on training rows only. The target coverage was 90% ($\alpha=0.1$), with 95% and 80% as checks. Each configuration was repeated over 10 random 60/20/20 splits (20 for the fresh set).

**What we report.** The main quantity is the *coverage on new cases*, compared with the promised 90%. We also report coverage on seen cases, the average set size or interval width, and the fraction of individual splits in which coverage on new cases fell below 87%. Data sets, not splits, are the unit of analysis. For tests across data sets we use Wilcoxon signed-rank tests with Holm's correction (Wilcoxon 1945; Holm 1979), Spearman rank correlations, and bootstrap confidence intervals over data sets.


# Results I: three applications

Table 1 summarizes the applications, using random forests (RF) and LightGBM, and Fig. 1 shows the random-forest results at a glance. The "Seen share" and "Predicted" columns need only the data. The other columns come from 10 random splits. Results for the linear model are in the Supplementary Material (Table R1).

![**Fig. 1** Coverage of 90% prediction sets in the three applications (random forest, mean of 10 random splits). Ticks: overall coverage as reported by the usual check; circles: coverage on new cases with standard calibration; diamonds: coverage on new cases after the fix (separate calibration). Vertical line: the promised 90%](Fig_cases.png)

**Software-defect prediction.** The two largest NASA sets, mc1 and pc2, consist mostly of repeated modules: with a random split, about 82% of the test modules in mc1 have an exact copy in the training data. The usual evaluation looks fine. The random forest's 90% sets were right for 91.7% of test modules in mc1 and 91.0% in pc2. On genuinely new modules they were right only 62.7% and 62.5% of the time. The check flags both sets before any model is trained: its predicted worst-case gaps are −42.8 and −38.8 percentage points (pp). The actual gaps are smaller than this worst case, as expected for a model that does not memorize perfectly, but they are of the same order. Separate calibration brings coverage of new modules back to 90.3% and 89.4%.

The new modules also show *why* the standard sets fail. On new mc1 modules the average set size was 0.63, so many sets were *empty*: the model was so confident about familiar-looking inputs that, for new ones, it offered no label at all. After the fix the average size is 0.91. For a review team, an empty set is a silent failure. A set that contains both labels is an honest "we don't know", which can be routed to manual inspection.

The smaller defect sets show the other side. The check predicts a gap of 2 pp or less for six of them. In five (pc1, pc3, pc4, jm1, mw1), coverage on new modules stayed within about 2 pp of 90% (88.1–89.6%), the fix changed little, and the check correctly signalled that standard conformal prediction was adequate. The sixth, kc2 (522 modules), is a miss: the predicted gap was only −1.4 pp, but new modules were covered at 86.7% (89.6% after the fix). Its exposure, however, is high (30% of test modules are seen), which is why we recommend reading exposure alongside the predicted gap (Section 8.1).

**Network-intrusion detection.** The KDD Cup'99 data repeat the same connection records thousands of times, and about 61% of test connections have a training copy. The standard 90% sets covered 95.5% of all test connections but 88.6% of new ones. With separate calibration, new-connection coverage was 91.6%. Overall coverage above 90% is itself a warning sign here: thousands of identical calibration records produce tied scores, which makes the standard method conservative overall while it under-covers the new connections.

**Phishing detection.** In the PhishingWebsites data, websites are described by 30 coarse features, so different sites often share the same profile. About 57% of test sites have a training copy. Overall coverage was 89.9%, coverage on new sites 84.8%, and 90.1% after the fix.

Across the 6 data sets that the check flagged (predicted gap worse than −2 pp), the random forest's coverage on new cases ranged from 62.5–89.8% before the fix and 89.4–94.5% after it. A flag is a warning, not a certainty. The small kc3 set was flagged (−4.9 pp), but its new modules were covered at 89.8% even without the fix. Here the standard sets were conservative overall (93.1%), most likely because many identical calibration rows produce tied scores (see the intrusion data below), and this offset the expected shortfall. The fix then simply made the sets a little more cautious (94.5%). The cost is modest in general: new cases get somewhat larger sets, while seen cases keep small ones.

**Table 1** Applications at a target of 90% coverage. Seen share: fraction of test rows with an exact training copy (from the check). Predicted: worst-case shortfall $g^*$ from Eq. (3), computed without training. Overall: coverage reported by the usual check. New (standard) and New (fixed): coverage on new cases without and with separate calibration. Set size: average set size for new cases, standard → fixed. Means over 10 random splits

| Application | Data set | Model | Seen share | Predicted (pp) | Overall (%) | New, standard (%) | New, fixed (%) | Set size |
|---|---|---|---|---|---|---|---|---|
| Network intrusion | KDDCup99 | RF | 0.61 | −15.7 | 95.5 | 88.6 | 91.6 | 0.89 → 0.92 |
| Network intrusion | KDDCup99 | LightGBM | 0.61 | −15.7 | 98.0 | 95.9 | 96.0 | 9.40 → 7.30 |
| Phishing websites | PhishingWebsites | RF | 0.57 | −12.0 | 89.9 | 84.8 | 90.1 | 0.85 → 0.92 |
| Phishing websites | PhishingWebsites | LightGBM | 0.57 | −12.0 | 89.9 | 90.4 | 90.0 | 0.91 → 0.91 |
| Software defects | mc1 | RF | 0.82 | −42.8 | 91.7 | 62.7 | 90.3 | 0.63 → 0.91 |
| Software defects | mc1 | LightGBM | 0.82 | −42.8 | 90.5 | 70.1 | 90.3 | 0.71 → 0.92 |
| Software defects | pc2 | RF | 0.81 | −38.8 | 91.0 | 62.5 | 89.4 | 0.63 → 0.91 |
| Software defects | pc2 | LightGBM | 0.81 | −38.8 | 89.8 | 72.8 | 89.6 | 0.74 → 0.91 |
| Software defects | kc1 | RF | 0.48 | −6.1 | 90.3 | 83.5 | 90.7 | 1.23 → 1.48 |
| Software defects | kc1 | LightGBM | 0.48 | −6.1 | 90.4 | 83.3 | 90.3 | 1.25 → 1.50 |
| Software defects | kc3 | RF | 0.33 | −4.9 | 93.1 | 89.8 | 94.5 | 1.10 → 1.25 |
| Software defects | kc3 | LightGBM | 0.33 | −4.9 | 92.6 | 89.3 | 94.7 | 1.12 → 1.33 |
| Software defects | kc2 | RF | 0.30 | −1.4 | 89.3 | 86.7 | 89.6 | 1.26 → 1.33 |
| Software defects | kc2 | LightGBM | 0.30 | −1.4 | 88.7 | 85.6 | 89.9 | 1.25 → 1.36 |
| Software defects | jm1 | RF | 0.22 | −1.8 | 89.8 | 88.2 | 89.4 | 1.28 → 1.33 |
| Software defects | jm1 | LightGBM | 0.22 | −1.8 | 89.4 | 87.8 | 89.7 | 1.28 → 1.34 |
| Software defects | pc1 | RF | 0.17 | −1.9 | 89.4 | 88.1 | 88.9 | 0.93 → 0.94 |
| Software defects | pc1 | LightGBM | 0.17 | −1.9 | 89.3 | 87.9 | 89.1 | 0.93 → 0.95 |
| Software defects | pc3 | RF | 0.10 | −1.1 | 89.9 | 89.3 | 90.0 | 1.01 → 1.02 |
| Software defects | pc3 | LightGBM | 0.10 | −1.1 | 90.1 | 89.4 | 90.3 | 1.02 → 1.04 |
| Software defects | pc4 | RF | 0.10 | −1.0 | 90.2 | 89.3 | 90.3 | 1.01 → 1.03 |
| Software defects | pc4 | LightGBM | 0.10 | −1.0 | 89.6 | 88.7 | 89.4 | 0.99 → 1.00 |
| Software defects | mw1 | RF | 0.08 | −0.7 | 89.5 | 89.6 | 90.0 | 1.00 → 1.00 |
| Software defects | mw1 | LightGBM | 0.08 | −0.7 | 89.9 | 90.1 | 89.6 | 1.01 → 0.99 |


# Results II: how often does it matter?

## Benchmark data: usually fine, occasionally not

Repeated rows are everywhere in the benchmarks. Of the 103 data sets, 53 contain at least one repeated feature vector, and in 11 at least 30% of rows belong to a group of identical rows. The exposure formula (2) predicted the share of seen test rows almost exactly (mean absolute error 0.0012, correlation 0.9998 with the share observed over 10 random splits), so this part of the check can be trusted. Per-data-set statistics are in the Supplementary Material (Table S1).

The effect on coverage, however, is usually small. We had planned to test whether the *typical* data set with repeats shows a shortfall on new cases, and it does not. The median gap from 90% across data sets was between −0.8 and +2.6 percentage points, depending on the learner and score, and none of these one-sided tests was significant after correction for multiple testing (smallest adjusted $p$ = 0.092). For most benchmark data, standard conformal prediction is adequate for new cases too.

The shortfalls are concentrated where the check says they should be. Where fewer than 10% of test rows are seen, no learner fell more than 2 pp short. Where at least 30% are seen, 31% of data set–learner combinations fell more than 2 pp short and 19% more than 5 pp. The worst case was −6.9 pp in classification and −16.9 pp in regression. These shortfalls are invisible in the usual overall figure, which stayed at 90% throughout.

Exposure alone does not explain which data sets fail; label purity does much of the rest. Two data sets with the same high exposure show the contrast. In *solar_flare* (about 85% seen test rows) new cases were covered only 73–79% of the time, depending on the learner. In *cps88wages*, with the same exposure, identical worker profiles almost always have different wages, so there is nothing to memorize, and new cases were covered at the nominal rate (89–91%). Across the 41 data sets with repeats, the predicted shortfall $g^*$ of Eq. (3) ranked the observed random-forest shortfalls well (Spearman $\rho$ = 0.72, against 0.51 for exposure alone). It also worked as a floor: in 97.6% of data sets the observed gap was no worse than $g^*$ minus 2 pp, and the typical random forest reached 0.84 of the predicted worst case. Less flexible learners fell short by less, as expected: LightGBM (0.49) and the neural network (0.62) were ranked reasonably, while for logistic regression exposure alone was the better guide (0.64 versus 0.45). We note that this analysis was done on data we had already seen when deriving Eq. (3). The fair test is in Section 7.

The one clear exception is *solar_flare* itself, where the random forest fell about 16 pp short although $g^*$ is only about −4 pp. Its repeated rows disagree on the exact target value, so they do not count as "pure", but the targets differ so little that the model still predicts them almost perfectly. This is precisely the failure of the equal-difficulty assumption mentioned in Section 3. In regression, a practitioner should therefore read the exposure $\bar\pi$, not only $g^*$, as a warning.

## Adding copies on purpose

The benchmark comparison is observational, so we also created the problem deliberately. Appending exact copies to the duplicate-free data sets raised exposure as Eq. (2) predicts, and the shortfall grew with it (Fig. 2). For random forests in classification, the median gap went from +0.1 pp without copies to −6.1 pp when half of the rows were copied and −12.8 pp when all were (regression: −11.8 pp). LightGBM behaved similarly (−7.9 pp). Regularized linear models, which do not memorize individual rows, were barely affected (−0.8 pp). In these experiments the predicted shortfall tracked the random-forest gap closely (Spearman $\rho$ = 0.87; median ratio of observed to predicted 0.81 at the highest rate). Separate calibration stayed at the target at every rate (+0.3 pp for random forests with all rows copied).

We also tried to show the other half of the mechanism by making models less flexible (larger leaves, stronger regularization) on the benchmark data. Coverage of seen rows did drop, as expected, but the change in the new-case gap was too small to detect at these data sets' moderate exposure (trend tests $p$ = 0.948 and 0.814 for random forests). We therefore rely on the learner comparison in the injection experiment, not on this experiment, for the role of model flexibility.

![**Fig. 2** Copies added on purpose to data sets without repeats: median coverage gap on new cases (coverage − 90%) against the share of rows copied, for standard calibration (solid) and separate calibration (dotted)](Fig_inject.png)

## What the fix costs

Separate calibration restored coverage on new cases across the board. On the benchmark data with repeats, its median gap ranged from −0.1 to +0.3 pp, and the confidence interval of the median stayed above −1 pp in all learner–score combinations. Its worst single data set was again solar_flare (−5.8 pp, against −16.9 pp for the standard method). That data set leaves only about 36 new calibration rows per split, and in 200 extra splits separate calibration averaged 90.9% (95% CI 89.9–91.8%) for LightGBM while the standard method averaged 78%.

This is where the safety margin of Section 3.4 helps: it trades a slightly larger set for protection against an unlucky calibration draw. Its effect on the fresh data is reported in Section 7.

The price in set size is modest. For new cases, sets or intervals grew by a median factor of 0.995–1.044, while seen cases received tighter sets, so the average over all cases changed by a factor of only 0.987–1.009. Computationally the fix is free: on 30,000-row data, hashing the rows took at most 0.16 s, and computing the two thresholds took 44 µs against 14 µs for one threshold. On data without repeats the fix reduces to the standard method exactly (largest difference 0).

Two alternatives are worth knowing. In regression, scaling residuals by the distance to the nearest training rows removed most of the shortfall on its own (median gap +0.1 pp for random forests), though without a guarantee for new cases and with a remaining worst case of −3.4 pp. Splitting the data so that identical rows always stay together (a "group split") also gives honest coverage for new cases (median 89.8–90.5%). It changes the training data, though, and it answers only the question "how good is the model on new cases", whereas separate calibration keeps the usual split and covers any mix of seen and new cases.


# Results III: fresh data and near-copies

## A fair test on data we had not seen

The predicted-gap formula (3) was derived after we had seen the benchmark results, so the analyses above could flatter it. We therefore fixed the analysis plan in a time-stamped commit and then selected new data sets from two collections we had not used: the AutoML Benchmark (Gijsbers et al. 2024) and the tabular benchmark of Grinsztajn et al. (2022). The selection used no labels and no models. It kept data sets in which at least 1% of test rows are expected to be seen, and it dropped data sets we had already used, data sets that appear twice in these collections, and five whose download failed. This left 20 data sets (8 classification, 12 regression), each analysed with 20 random splits. The full selection log, with the reason for every exclusion, and per-data-set results are in the Supplementary Material (Tables R2–R7). The plan named five tests in advance. Two were clearly supported and three were not, and we report all five.

*The fix works on new data.* Separate calibration kept the coverage of new cases at the target for all three learners. The median gap was 0.0 pp for random forests (worst data set −0.7 pp), 0.0 pp for LightGBM (worst −0.9 pp) and 0.0 pp for the linear models (worst −0.5 pp). Without the fix, the worst data set's gap was −27.5 pp (random forest) and −33.3 pp (LightGBM). The fix made new-case sets larger by a median factor of only 1.00, because on most of these data sets there was little to fix. In one data set (seattlecrime6) almost every test row is seen, and the fix returned the full set for new cases in 75.0% of splits, because too few new calibration rows existed to do anything else.

*The safety margin reduces unlucky splits.* With separate calibration, coverage of new cases fell below 87% in 4.2% of individual splits (random forest). With the safety margin this dropped to 0.5%, and similarly for the other learners (4.5% → 0.8% and 4.8% → 0.5%). The cost was sets about 1.04 times as large. Because most data sets had no unlucky splits at all, this planned test did not reach significance after correction for multiple testing (adjusted $p$ = 0.062).

*The predicted gap works as a limit, not as a ranking.* In all 20 data sets, the random forest's actual gap stayed within 2 pp of the predicted worst case or above it (100.0%; 95% CI 83.2–100.0%), as planned. LightGBM behaved the same, and the linear models had one exception, discussed below. However, the predicted gap did **not** rank the fresh data sets by how badly they fell short: the planned rank correlation for random forests was weak and not significant ($\rho$ = 0.12, $p$ = 0.307), and the advantage over exposure alone was not established (difference in $\rho$, 95% CI −0.06 to 0.83). For LightGBM the correlation was 0.39 ($p$ = 0.043, not corrected). Two things explain this. Most fresh data sets have essentially no shortfall, so their ranks are decided by noise. And on some of the most exposed classification sets the random forest was *conservative* on new cases instead of falling short. On airlines, for example, the predicted worst case was −5.5 pp but the observed gap was +8.7 pp, most likely because many identical calibration rows produce tied scores (Section 5).

*The check tells safe from unsafe data.* For a practitioner, ranking matters less than the decision "fix or not". Here the check did well (Fig. 4). Before these results existed, our draft guidance said that a data set with a predicted gap no worse than −2 pp and fewer than 10% seen test rows needs no fix (Section 8.1). Of the fresh data sets, 9 met this rule, and the worst gap among them, over all three learners, was −1.0 pp. In the other direction, label purity removed false alarms that exposure alone would raise. In black_friday (63% seen test rows), seattlecrime6 (100%) and superconduct (33%), repeated rows almost never agree on the exact target, so purity predicts no shortfall even though exposure alone predicts −17.1, −90.0 and −5.0 pp. The random forest's actual gaps were +1.8, +6.7 and −0.9 pp. Of the 10 data sets that exposure alone flags, the purity-based check flags 6, and among these are all data sets where the random forest or LightGBM fell more than 2 pp short (3 and 4 data sets). The clearest case is analcatdata_supreme, where 81% of test rows have a training copy with exactly the same target. The check predicted a worst case of −42.4 pp, and the observed gaps on new cases were −27.5 pp (random forest) and −33.3 pp (LightGBM).

The one miss was a linear model on black_friday, whose gap was −3.7 pp although the purity-based check predicted no problem. A linear model cannot memorize rows, so this shortfall is not the memorization effect the check is built for; exposure alone did flag this data set. This again suggests reading both numbers, as recommended in Section 8.1.

![**Fig. 4** Fresh data sets, random forest. For each data set where exposure alone predicts a gap worse than −2 pp: the gap predicted from exposure only (circles), the gap predicted with label purity, Eq. (3) (diamonds), and the observed gap on new cases (ticks). Shaded: within 2 pp of the target](Fig_fresh.png)

## When copies are not exact

Real duplicates are often not byte-identical: a value is rounded differently, or a record is re-measured. To see what this does, we appended copies of half of the rows to each of the same 37 duplicate-free data sets and added a little noise to the copies' numeric features, from none up to 10% of each feature's standard deviation. Because we created the copies ourselves, we know which test rows are *truly* new, meaning that no version of the same record is in the training data.

Even very small noise blinds the exact-match check: at every noise level above zero it recognized none of the copies (0.0%; Fig. 5). The problem itself does not go away, though. With exact copies, the random forest's coverage gap on truly new cases was −5.8 pp in classification. With noise of 0.1%, 1% and 10% of a standard deviation, it was −4.3, −3.6 and −2.7 pp (regression: −5.2, −4.1, −3.3 and −0.8 pp). Small amounts of noise leave most of the shortfall in place; only noise of 10% of a standard deviation removes most of it in regression. The exact-match fix cannot see these copies: once noise is added, its result is close to that of the standard method (−4.1 pp at the smallest noise level in classification).

Calibrating by *distance* to the nearest training rows does handle this case. We split calibration and test rows into six groups by that distance (exact copies form one group) and calibrated each group separately. Coverage of truly new cases then stayed at the target at every noise level (+0.5, +0.2, +0.1 and +0.5 pp in classification; +0.7, +0.2, +0.1 and +0.5 pp in regression), as good as an idealized version that knows the true record identity (0.0 pp at 1% noise). In practice, then, the exact check is the right first step because it is simple and explains *why* coverage fails, and distance-based calibration is the safer fix whenever near-copies are plausible.

![**Fig. 5** Copies with added noise (random forest, median over 37 data sets; half of the rows copied). Coverage gap on truly new cases, in percentage points, for the standard method, the exact-match fix, the distance-based fix, and a reference that knows which records were copied](Fig_neardup.png)


# Discussion

## What a practitioner should do

The results suggest a short routine for anyone who reports conformal prediction on tabular data.

1. **Check before training.** Hash the feature vectors, compute the expected share of seen test rows $\bar\pi$ with Eq. (2) and the label-pure share $\pi_P$, and from it the predicted shortfall $g^*$ of Eq. (3). This takes seconds and needs no model. In our data, a predicted shortfall smaller than about 2 pp together with an exposure below 10% reliably meant that nothing needed to change.
2. **Fix if flagged.** If the predicted shortfall is larger, or exposure is high, calibrate seen and new cases separately. When fewer than a few hundred new calibration rows are available, add the safety margin of Section 3.4. In regression, a distance-scaled residual is a sensible additional step.
3. **Report both numbers.** Give coverage on new cases next to overall coverage, and say how many test rows were seen. A reader can then judge the evaluation without rerunning it.

The routine matters most where a model will meet records it has never seen: a new software module, a new network connection, a new website. In these settings the reported coverage is used to make decisions, such as how many modules to send to manual review or which alerts to escalate. An empty prediction set for a new defect-prone module, as we saw on mc1, is a silent failure that no overall coverage figure reveals.

## Should one simply remove duplicates?

A common first reaction is to delete repeated rows before analysis. That is not always right. If the same input really does recur in deployment, for example a frequent network connection pattern, then repeats are part of the population, and deleting them changes the question being answered. Deleting repeats with conflicting labels also throws away information about label noise. Where records arrive over time, a time-based split (Sheridan 2013) is another honest evaluation, but it answers a different question again. Separate calibration avoids the choice: it keeps the data as they are and gives a valid promise for seen and for new cases, so the user can weight the two according to what is expected in deployment.

## Limitations

*Exact matches only.* The check detects only rows with identical feature values. Near-copies, such as the same record with a rounding difference or a re-measured value, are invisible to it. In our perturbation experiment, the exact-match check found none of the perturbed copies, and the remaining shortfall then had to be handled by distance-based calibration (Section 7.2). In practice the hashing can be made coarser (for example, by rounding features), but choosing that resolution is a modelling decision.

*The predicted shortfall is a worst case with known failure modes.* Eq. (3) assumes a model that memorizes pure repeats perfectly and finds all other rows equally hard. Regularized models fall short by less than predicted, which is harmless. The opposite case, where repeated rows that disagree slightly on a regression target are still easy (solar_flare), can make the actual shortfall much larger than predicted. We therefore recommend looking at exposure as well as at $g^*$. On fresh data, the predicted gap worked as a limit and as a screen for which data sets need the fix, but it did not rank data sets by the size of their shortfall (Section 7.1). It should be read as a warning level, not as a forecast of the exact coverage.

*The typical benchmark is not affected.* Our planned test of a general shortfall across benchmark data sets with repeats was negative, and our attempt to show the role of model flexibility by varying it within a learner was inconclusive. The problem is real but concentrated. We present the check precisely because it tells the two situations apart.

*Seen rows are defined by the training data.* Coverage on held-out new rows equals coverage on genuinely new records only if future records come from the same population. If deployment brings a distribution shift, separate calibration does not help with that; weighted or shift-aware conformal methods are needed (Tibshirani et al. 2019; Barber et al. 2023).

*Group splits and small calibration sets.* With very few new calibration rows (around 30), separate calibration is valid on average but noisy from split to split. The safety margin addresses this at the price of larger sets, and if no valid threshold exists it returns the full set, which is the honest answer.

*How the study was done.* The study, including its code and much of its text, was produced with substantial help from an AI system under human direction (see Declarations). Every number in the paper is computed by released code from archived result files. The fresh validation analysis was fixed in a time-stamped commit before its data were collected, and deviations from that plan are recorded in the repository.


# Conclusion

Conformal prediction promises that its sets contain the right answer a stated share of the time, and practitioners check that promise on a random test split. When the data contain repeated rows, this check mixes cases the model has already seen with genuinely new ones, and it can report 90% while new cases are covered far less often. We showed how to predict the size of this problem from the data alone, before any model is trained, and how to remove it by calibrating seen and new cases separately. On software-defect, intrusion and phishing data, and on fresh data sets analysed under a plan fixed in advance, the fix brought coverage of new cases back to about the target. On most standard benchmarks the check correctly reported that nothing needed to change. The procedure takes seconds, adds two lines to an evaluation report, and turns a hidden failure into a visible and repairable one. Extending the check from exact to near-identical records is the most useful next step.


# Appendix A: Derivations {-}

**Setting.** The rows of $D$ are split uniformly at random into $T$, $C$ and $E$. Given the set of training rows, the remaining rows are still split at random between $C$ and $E$, so for any test row $j$ the rows of $C\cup\{j\}$ are exchangeable. Whether a row is "seen" depends only on the training rows, so it is a fixed label once $T$ is given. These two facts are all that the arguments below need.

**Equation (1).** By the law of total probability, $c=\pi c_S+(1-\pi)c_N$; solve for $c_N$. Split conformal prediction gives $1-\alpha\le c\le 1-\alpha+1/(n_C+1)$ when scores have no ties (Lei et al. 2018). Hence the miscoverage on new cases, $m_N=1-c_N$, satisfies
$$\frac{\alpha-1/(n_C+1)-\pi m_S}{1-\pi}\le m_N\le \frac{\alpha-\pi m_S}{1-\pi},$$
with $m_S=1-c_S$. Exact duplicates in the calibration set create tied scores. Ties keep the lower bound on coverage but can break the upper one.

**Equation (2).** Given that row $j$ is a test row, the training set is a random $n_T$-subset of the other $N-1$ rows. Row $j$ is new exactly when none of the other $m_g-1$ rows of its group is chosen, which has probability $\binom{N-m_g}{n_T}/\binom{N-1}{n_T}\approx(1-n_T/(N-1))^{m_g-1}$. Averaging over test rows gives Eq. (2).

**Equation (3).** Call a row *memorizable* if its training copies all carry exactly its label, and let $\pi_P$ be the probability that a calibration or test row is memorizable. Assume (M) that memorizable rows receive score 0, and (E) that all other rows have scores from a common continuous distribution $F$. Calibration scores then come from the mixture $\pi_P\delta_0+(1-\pi_P)F$, and as $n_C\to\infty$ the conformal threshold converges to its $(1-\alpha)$-quantile. For $\pi_P<1-\alpha$, this is the point $t$ with $\pi_P+(1-\pi_P)F(t)=1-\alpha$, so non-memorizable rows, and in particular new rows, are covered with probability $F(t)=1-\alpha/(1-\pi_P)$. For $\pi_P\ge 1-\alpha$ the threshold is 0 and new rows are almost never covered. In a simulation with $\pi_P=0.4$ and 1,000 calibration rows (800 repetitions), the average coverage of non-memorizable rows was within 0.01 of $1-0.1/0.6=0.833$ (unit test `test_purity_limit_simulation`).

**Separate calibration (the fix).** Let $\hat q_k$ be the $\lceil(n_k+1)(1-\alpha)\rceil$-th smallest calibration score among the $n_k$ calibration rows of category $k\in\{\text{seen},\text{new}\}$ ($+\infty$ if this rank exceeds $n_k$). Condition on $T$, on the category of test row $j$ and on the set of category-$k$ rows in $C\cup\{j\}$. Each of these $n_k+1$ rows is then equally likely to be the test row, so the usual rank argument gives $\Pr\{Y_j\in\mathcal C(X_j)\mid \text{category }k\}\ge 1-\alpha$ for each $k$ (Vovk et al. 2022). Any mix of seen and new cases at deployment is a weighted average of two quantities that are each at least $1-\alpha$.

**Safety margin.** With continuous scores, the coverage obtained by using the $r$-th smallest of $n$ calibration scores as threshold follows a Beta$(r,n-r+1)$ distribution over calibration draws. Taking the smallest $r$ with $\Pr\{\text{Beta}(r,n-r+1)<1-\alpha\}\le\delta$ gives coverage of at least $1-\alpha$ with probability at least $1-\delta$ (Vovk 2012). We use $\delta=0.1$.


# Statements and Declarations {-}

**Competing interests.** [AUTHOR TO CONFIRM: The authors declare that they have no known competing financial or non-financial interests.]

**Funding.** [AUTHOR TO CONFIRM: No funding was received for conducting this study.]

**Author contributions.** [AUTHOR TO COMPLETE, e.g. in CRediT format, after the author list is fixed.]

**Ethics approval.** Not applicable. The study uses only public, de-identified data sets from OpenML and involves no human participants or animals.

**Data availability.** All data sets are public and are identified by their OpenML identifiers in the Supplementary Material. All per-split results, tables and statistics behind the reported numbers are included in the code repository.

**Code availability.** The complete pipeline (check, experiments, statistics, figures and manuscript build) is available as a version-controlled repository, and one command reproduces every reported number. [AUTHOR TO COMPLETE: archive the repository with a DOI (e.g. Zenodo) and insert the link.]

**Use of AI tools.** The study design, literature search, code, experiments, statistical analysis and drafting of this manuscript were carried out with substantial assistance from an AI system (a large language model working with code-execution tools), under the direction of the human author(s). The text was revised for readability with the same assistance. All numerical results were produced by executed code whose outputs are archived with the repository. The human author(s) checked the work and take full responsibility for its content. [AUTHOR TO CONFIRM wording against the journal's current AI policy.]


# References {-}

Allamanis M (2019) The adverse effects of code duplication in machine learning models of code. In: Proceedings of the 2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software (Onward! 2019), pp 143–153. https://doi.org/10.1145/3359591.3359735

Angelopoulos AN, Bates S (2023) Conformal prediction: a gentle introduction. Found Trends Mach Learn 16(4):494–591. https://doi.org/10.1561/2200000101

Barber RF, Candès EJ, Ramdas A, Tibshirani RJ (2023) Conformal prediction beyond exchangeability. Ann Stat 51(2):816–845. https://doi.org/10.1214/23-AOS2276

Barz B, Denzler J (2020) Do we train on test data? Purging CIFAR of near-duplicates. J Imaging 6(6):41. https://doi.org/10.3390/jimaging6060041

Bastani O, Gupta V, Jung C, Noarov G, Ramalingam R, Roth A (2022) Practical adversarial multivalid conformal prediction. In: Advances in Neural Information Processing Systems 35, pp 29362–29373. https://doi.org/10.52202/068431-2129

Bischl B, Casalicchio G, Feurer M, Gijsbers P, Hutter F, Lang M, Mantovani RG, van Rijn JN, Vanschoren J (2021) OpenML benchmarking suites. In: Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks 1. arXiv:1708.03731

Boström H, Johansson U (2020) Mondrian conformal regressors. In: Proceedings of the Ninth Symposium on Conformal and Probabilistic Prediction and Applications, PMLR 128:114–133

Breiman L (2001) Random forests. Mach Learn 45(1):5–32. https://doi.org/10.1023/A:1010933404324

Deng J (2026) When identical rows disagree: from benchmark identifiability to replication-robust anomaly detection. arXiv:2609.29580 (preprint, not peer reviewed)

Ding T, Angelopoulos AN, Bates S, Jordan MI, Tibshirani RJ (2023) Class-conditional conformal prediction with many classes. In: Advances in Neural Information Processing Systems 36. arXiv:2306.09335

Dunn R, Wasserman L, Ramdas A (2023) Distribution-free prediction sets for two-layer hierarchical models. J Am Stat Assoc 118(544):2491–2502. https://doi.org/10.1080/01621459.2022.2060112

Elangovan A, He J, Verspoor K (2021) Memorization vs. generalization: quantifying data leakage in NLP performance evaluation. In: Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics, pp 1325–1335. https://doi.org/10.18653/v1/2021.eacl-main.113

Fischer SF, Feurer M, Bischl B (2023) OpenML-CTR23 – a curated tabular regression benchmarking suite. In: AutoML Conference 2023 (Workshop Track). OpenML study 353

Foygel Barber R, Candès EJ, Ramdas A, Tibshirani RJ (2021) The limits of distribution-free conditional predictive inference. Inf Inference 10(2):455–482. https://doi.org/10.1093/imaiai/iaaa017

Gibbs I, Cherian JJ, Candès EJ (2025) Conformal prediction with conditional guarantees. J R Stat Soc Ser B Stat Methodol 87(4):1100–1126. https://doi.org/10.1093/jrsssb/qkaf008

Gijsbers P, Bueno MLP, Coors S, LeDell E, Poirier S, Thomas J, Bischl B, Vanschoren J (2024) AMLB: an AutoML benchmark. J Mach Learn Res 25(101):1–65

Gray D, Bowes D, Davey N, Sun Y, Christianson B (2011) The misuse of the NASA metrics data program data sets for automated software defect prediction. In: 15th Annual Conference on Evaluation & Assessment in Software Engineering (EASE 2011), pp 96–103. https://doi.org/10.1049/ic.2011.0012

Grinsztajn L, Oyallon E, Varoquaux G (2022) Why do tree-based models still outperform deep learning on typical tabular data? In: Advances in Neural Information Processing Systems 35 (Datasets and Benchmarks Track). https://doi.org/10.52202/068431-0037

Guan L (2023) Localized conformal prediction: a generalized inference framework for conformal prediction. Biometrika 110(1):33–50. https://doi.org/10.1093/biomet/asac040

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

Tareaf RB, Al-Rajab M, Loucif S, Ellaham S, Schmitz C (2026) Target leakage, not model class, explains reported accuracy in survey-based cardiovascular screening. arXiv:2609.11838 (preprint, not peer reviewed)

Tavallaee M, Bagheri E, Lu W, Ghorbani AA (2009) A detailed analysis of the KDD CUP 99 data set. In: 2009 IEEE Symposium on Computational Intelligence for Security and Defense Applications, pp 1–6. https://doi.org/10.1109/CISDA.2009.5356528

Tibshirani RJ, Barber RF, Candès EJ, Ramdas A (2019) Conformal prediction under covariate shift. In: Advances in Neural Information Processing Systems 32. arXiv:1904.06019

Vanschoren J, van Rijn JN, Bischl B, Torgo L (2014) OpenML: networked science in machine learning. SIGKDD Explor 15(2):49–60. https://doi.org/10.1145/2641190.2641198

Vovk V (2012) Conditional validity of inductive conformal predictors. In: Proceedings of the Asian Conference on Machine Learning, PMLR 25:475–490

Vovk V, Gammerman A, Shafer G (2022) Algorithmic learning in a random world, 2nd edn. Springer, Cham. https://doi.org/10.1007/978-3-031-06649-8

Wilcoxon F (1945) Individual comparisons by ranking methods. Biometrics Bull 1(6):80–83. https://doi.org/10.2307/3001968

Zhang R, Zhou P (2026) A Mondrian conformal predictive system with improved decision trees for uncertainty quantification under heteroscedasticity. Pattern Recognit 172:112338. https://doi.org/10.1016/j.patcog.2025.112338
