# Review 11: Pattern Recognition associate editor and methods reviewer (re-targeting round)

A role-separated pass by the same AI system, simulating an Associate Editor and a
conformal-prediction methods reviewer at Pattern Recognition. It is **not** an independent human
review.

## R11.1 [MAJOR]: Would a locally adaptive score already solve the problem?
**Concern.** Normalized or difficulty-adaptive scores (Papadopoulos et al. 2011) shrink intervals
near training data, so they may absorb the duplicate effect, making the Mondrian remedy
unnecessary.
**Action.** New baseline, pre-specified before outcomes (protocol deviation #6): a kNN-normalized
residual on all 12 duplicated regression datasets, with RF and LightGBM, 10 seeds.
**Outcome (reported in the Results, Discussion, Abstract and Conclusion).** The normalized score
removes most of the shortfall: worst gap −3.4/−2.6 pp versus −15.8/−16.9 pp with the absolute
residual; median ≈ 0. Mondrian on top adds no systematic gain. The paper now presents adaptive
scores as an effective heuristic mitigation and novelty-Mondrian calibration as the option with
a guarantee.
**Status.** Fixed with new evidence. This **weakens** the claim that Mondrian calibration is
needed, and the manuscript says so.

## R11.2 [MAJOR]: Novelty for a methods journal
**Concern.** Pattern Recognition publishes new conformal methods; this paper's method is standard.
**Response.** The contribution is positioned as an exact characterization plus an
evaluation-methodology finding, with external and causal evidence, which suits the journal's
recent conformal-prediction line (two Mondrian papers in 2026). The risk remains.
**Status.** Residual risk HIGH for this venue. The cascade plan is in
`journal_selection/selected_journal.md`.

## R11.3 [MODERATE]: Formatting
Numbered references, highlights (5, ≤ 79 characters), abstract ≤ 250 words, keywords ≤ 7,
author-biography placeholder, generative-AI declaration, and a 31-page review-format build
(limit 20–35).
**Status.** Fixed.

## R11.4 [MODERATE]: Cite the journal's related work
**Action.** Added three 2026 Pattern Recognition papers, with Crossref-verified metadata (Mondrian
CP for spatial modelling; Mondrian conformal predictive systems; CP under strong distribution
shift). They are described only from their titles, because their abstracts were not accessible.
**Status.** Fixed; the authors should read these papers before submission.

## R11.5 [MINOR]: Classification analogue of the normalized score
No standard distance-normalized classification score exists. The distance-Mondrian variant is
reported as exploratory.
**Status.** Disclosed.
