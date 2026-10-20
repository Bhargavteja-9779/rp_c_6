# Research problem, questions, hypotheses, contributions (Agents 0, 5, 8)

## Central problem

Split conformal prediction (CP) is reported with a finite-sample *marginal* coverage guarantee, and
standard practice evaluates it on random row-level splits. Many tabular data sets contain repeated
records: identical feature vectors from duplicated logging, repeated measurements, or enumerated
discrete profiles. Under a random row split, some test rows then have exact copies in the training
set. The guarantee is averaged over these "seen" rows and genuinely *novel* rows. **Does the
reported guarantee hold for novel records, which are the deployment-relevant case when new
entities arrive? If not, by how much does it fail, and which cheap remedy restores it?**

## Research questions

* **RQ1 (prevalence and exposure).** In two standard benchmark suites (OpenML-CC18 classification,
  OpenML-CTR23 regression), what fraction of test rows has a training copy under a standard random
  split? Is this exposure predicted by a label-free audit (Proposition 2)?
* **RQ2 (validity failure).** Under standard split CP, how far below the nominal level is coverage
  on novel test records? How does the gap depend on exposure π and on model family?
* **RQ3 (remedy).** Does novelty-Mondrian CP restore nominal coverage on novel records, and at what
  cost in set size or interval width? How does it compare with a group-aware (record-level) split?
* **RQ4 (calibration).** Are predicted probabilities over-confident on novel records even when
  overall calibration looks acceptable?
* **RQ5 (mechanism).** In controlled experiments that inject duplicates into duplicate-free data
  sets, and that vary model capacity, does the novel-record gap follow the dose–response predicted
  by Proposition 1?
* **RQ6 (exploratory).** Does the effect extend smoothly to near-duplicates, i.e. coverage as a
  function of distance to the nearest training record?

## Hypotheses (confirmatory unless marked)

* **H1** Under standard split CP (random split, α = 0.1), novel-record coverage is below 0.90 on
  data sets with non-trivial exposure (predicted π̄ ≥ 0.01).
  * **H1a** The gap grows with exposure (negative Spearman correlation between π and the gap).
  * **H1b** The gap is larger for higher-capacity / more memorizing learners (kNN, RF) than for
    regularized linear models.
* **H2** Novelty-Mondrian CP reaches novel-record coverage ≥ 0.90 − 0.01 (median over data sets),
  and higher than standard split CP.
* **H3** (two-sided, descriptive) Novelty-Mondrian enlarges sets or intervals for novel records and
  shrinks them for seen records. The overall average size changes little.
* **H4** Top-label expected calibration error (ECE) on novel test records exceeds the ECE computed
  on all test rows.
* **H5** In injection experiments the novel-record gap increases monotonically with the injected
  duplication rate. In capacity experiments it increases with capacity.
* **H6** Standard CP on a group-aware split attains approximately nominal coverage (median
  ≥ 0.90 − 0.01) on its all-novel test set.
* **Null control** On duplicate-free data sets, standard split CP reaches nominal coverage and
  the two methods coincide.

**Falsification.** H1 fails if the median novel gap is not significantly negative after Holm
correction. If so, the paper reports that duplication is practically harmless for CP validity, a
useful negative result. H2 fails if novelty-Mondrian under-covers novel records.

## Contributions (each with its verifying evidence)

1. Exact characterization of novel-record coverage under marginal calibration, including the
   α/(1 − π) memorization limit (Prop. 1). Verified by Experiments B and D.
2. A label-free exposure formula that predicts, from an audit alone, which data sets are at risk
   (Prop. 2). Verified by RQ1 (predicted vs observed π).
3. The first large-scale empirical quantification of duplicate-induced conditional miscoverage of
   CP and of calibration error on novel records, across 103 benchmark data sets, 5 model families
   and 4 nonconformity scores (Experiments A–C).
4. A remedy with a finite-sample guarantee for any deployment mix (Prop. 3, Cor. 1), evaluated
   against a group-aware split (Experiment C).
5. An open, tested audit and evaluation pipeline (`code/`).
