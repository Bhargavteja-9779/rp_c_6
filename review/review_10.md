# Review 10 — Final rejection attempt

This is a distinct adversarial pass carried out by the same AI system in a different reviewer role. It was **not** conducted by independent human reviewers.

## R10.1 [MAJOR (not fatal)]

**Concern.** The central claim could be judged weak because the primary test failed.

**Response / action.** The paper's claims are now proportional: the mechanism (exact), the predictability (exposure formula), the at-risk minority (suites + external + injection), the remedy. No claim of a typical shortfall remains.

**Files / experiments.** Abstract, Intro, Discussion

**Status.** Fixed

## R10.2 [MODERATE]

**Concern.** 'Pre-registered' implies an external registry.

**Response / action.** Reworded to 'pre-specified protocol committed to version control (not an external registry)'.

**Files / experiments.** all sections

**Status.** Fixed

## R10.3 [MODERATE]

**Concern.** Over-generalization: 'datasets with conflicting labels are unaffected' rests on one dataset.

**Response / action.** Narrowed to 'a dataset (cps88wages)'.

**Files / experiments.** 01_intro.md

**Status.** Fixed

## R10.4 [MODERATE]

**Concern.** Discussion claimed '5–17 points' for the NASA defect data, but kc1 shows 3–7.

**Response / action.** Replaced with exact, sourced figures (suites: up to 16.9 pp on solar_flare; external: up to 27.5 pp).

**Files / experiments.** 06_discussion.md

**Status.** Fixed

## R10.5 [MINOR]

**Concern.** Capacity half of H5 not supported.

**Response / action.** Reported as not supported, with explanation (underpowered at moderate exposure; k-NN ties).

**Files / experiments.** 05_results.md

**Status.** Disclosed
