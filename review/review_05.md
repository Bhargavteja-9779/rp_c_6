# Review 05 — Dataset and external validity

This is a distinct adversarial pass carried out by the same AI system in a different reviewer role. It was **not** conducted by independent human reviewers.

## R5.1 [MAJOR]

**Concern.** The curated suites under-represent duplicated data (CTR23 excludes datasets needing grouped splits).

**Response / action.** External validation set added (see R1.2).

**Files / experiments.** results/external

**Status.** Fixed with new evidence

## R5.2 [MODERATE]

**Concern.** KDD Cup'99 required uniform row subsampling, which departs from the group-preserving rule.

**Response / action.** Pre-specified and disclosed. Uniform subsampling keeps very large duplicate groups heavily duplicated.

**Files / experiments.** protocol_deviations.md #4

**Status.** Disclosed

## R5.3 [MODERATE]

**Concern.** Legitimate recurrence vs duplicate records: is the novel-row estimand right?

**Response / action.** Estimand discussion in Theory and Recommendations (choose the estimand deliberately).

**Files / experiments.** —

**Status.** Addressed
