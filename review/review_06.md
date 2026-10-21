# Review 06 — Baselines and fairness

This is a distinct adversarial pass carried out by the same AI system in a different reviewer role. It was **not** conducted by independent human reviewers.

## R6.1 [MODERATE]

**Concern.** No stronger conditional-coverage baseline (e.g. Gibbs et al. 2025).

**Response / action.** For the two disjoint groups considered, conditional calibration over group indicators reduces to Mondrian calibration, so it would coincide with MCP-R. CQR (an adaptive score) is included and still under-covers; the distance-Mondrian variant is included as exploratory.

**Files / experiments.** 02_related.md

**Status.** Addressed by argument

## R6.2 [MINOR]

**Concern.** Untuned learners.

**Response / action.** Fixed defaults pre-specified; capacity explicitly varied; disclosed in Limitations.

**Files / experiments.** —

**Status.** Disclosed
