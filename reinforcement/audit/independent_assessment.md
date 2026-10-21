# Independent scientific re-evaluation (Phase 2)

Read as if seeing the work for the first time, ignoring the earlier claims.

1. **What question does it answer?** When rows in a tabular dataset repeat, how does the
   held-out coverage of split conformal prediction relate to coverage on records that the model
   has not seen, and how can valid coverage for new records be obtained?
2. **What new knowledge does it establish?**
   (a) Novel-record coverage equals (c − π c_S)/(1 − π). This is an identity, so the new knowledge
   is not the identity itself but the measurement showing *when* the terms are large.
   (b) Exposure π is predictable almost exactly from group sizes (MAE 0.0012).
   (c) In two standard suites the shortfall is negligible for most datasets but large (up to
   17 pp; up to 27.5 pp in external defect data) where exposure is high **and** seen rows are
   over-covered.
   (d) In regression, a distance-normalized score absorbs most of the effect.
3. **What does the proposed method do that established methods do not?** Little. Novelty-Mondrian
   CP is standard Mondrian CP with a particular taxonomy. Its only distinctive property is the
   validity argument for a training-set-dependent taxonomy, which is short.
4. **Is the difference meaningful?** For datasets at risk, yes (5–28 pp of coverage). For most
   benchmark datasets, no.
5. **Type of contribution.** Mainly empirical and evaluation-methodological; light theory; the
   method is not new.
6. **New finding or reproduction?** New in the conformal setting. Duplicate leakage itself is
   known (Li 2026, Roth 2026, Deng 2026; Kapoor & Narayanan 2023).
7. **Does the evidence support the claims?** Mostly, after the previous cycle's narrowing. One
   unsupported generalization remains: *which* datasets fail is explained only post hoc, through
   the seen-coverage term c_S, which requires training a model. A practitioner cannot know in
   advance whether c_S will be inflated.
8. **Would the paper remain valuable if the effect disappeared?** Partly. The exposure formula
   and the negative primary result are still informative, but the practical motivation weakens.
9. **Contribution in three sentences (current).** "Duplicates split the conformal guarantee
   between seen and new records, by an amount we characterize exactly. The effect is negligible
   for most benchmark datasets but large for a predictable minority. A standard Mondrian
   calibration on the seen/novel taxonomy restores validity."
   The word "predictable" is only half true: exposure is predictable, but the seen over-coverage
   that determines the size of the gap is not, under the current analysis.
10. **Would a skeptical editor consider it substantial?** At a broad CS journal, plausibly. At a
    methods-focused Q1 journal, probably not without a sharper, non-trivial, predictive result.
11. **Could a simpler approach answer the question?** For regression, a normalized score largely
    does. A group-aware split also answers it, for an all-new deployment.
12. **Strongest legitimate rejection argument.** "This is known subgroup under-coverage of
    marginal CP, applied to an obvious grouping. The theory is a one-line identity, the remedy is
    textbook Mondrian CP, the primary hypothesis failed, and an off-the-shelf adaptive score
    already fixes regression. The work is a careful benchmark note, not a research contribution."

## Highest-impact weaknesses to address with new research (not with wording)

1. **No a-priori predictor of *which* datasets fail.** Exposure alone is not sufficient (cps88wages).
   Theory can supply the missing quantity: for a learner that reproduces the training labels of
   seen records, seen coverage is driven by **label purity** of duplicate groups, which is
   computable from the data before training. A purity-adjusted bound would turn the post-hoc
   decomposition into a testable, model-free risk prediction. It must then be validated
   **prospectively**, on datasets not yet examined.
2. **Remedy comparison is incomplete for classification and for small novel calibration sets.**
   The distance-Mondrian variant was only exploratory, and the split-to-split variability of
   novelty-Mondrian CP (SD ≈ 0.07 with ~36 rows) was noted but not addressed. A
   training-conditional (PAC-type) threshold is the principled fix and should be evaluated.
3. **Exact-duplicate restriction.** Real duplicates are often perturbed (rounding, jitter). The
   exact-key taxonomy cannot see them. Whether the mechanism and the remedy survive
   near-duplicates must be tested causally (controlled jittered injection), including the
   honest possibility that exact-key Mondrian fails there.
4. **External validity of conclusions drawn from the same 108 datasets used to develop the
   explanations.** A prospective validation set is needed.
