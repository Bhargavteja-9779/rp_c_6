# Reinforcement plan (Phase 6)

Prioritized by scientific impact × feasibility × risk reduction. Each item addresses entries in
`audit/rejection_risk_register.md`.

## U1. Purity-adjusted memorization limit (theory) and an a-priori risk predictor (R01, R02, R07, R08)

1. **Deficiency.** The paper explains which datasets fail only post hoc, through seen-row
   coverage c_S, which requires a trained model. Exposure alone mispredicts: cps88wages has π = 0.85
   and no gap.
2. **Evidence.** Fig. 3 of v1; the cps88wages vs solar_flare contrast; the strata analysis.
3. **Improvement.** Proposition 4. Define π_P, the share of test rows whose training copies all
   carry the test row's label (classification) or exactly its target value (regression). Assume
   (M) that the learner gives such rows the minimum score 0, and (E) that all other rows (novel,
   plus seen rows with conflicting labels) share one score distribution. Then, as the calibration
   size grows, novel-record coverage → max(0, 1 − α/(1 − π_P)). The predicted gap is
   g* = −α π_P/(1 − π_P), computable from labels and group structure **without training**.
4. **Hypothesis.** g* ranks datasets by their observed gap for flexible learners, and bounds the
   gap from below (up to noise). Regularized learners show only a fraction of g*.
5. **Implementation.** `audit.purity_exposure` (exact computation on the realised splits).
6. **Experiment.** Prospective validation (U4) plus retrospective analysis of the 108 existing
   datasets.
7. **Expected if true.** Strong rank correlation between g* and observed RF gaps; g* better than
   the exposure-only bound −απ/(1 − π).
8. **If false.** Report that seen-row label purity does not explain the gaps. The predictive claim
   is dropped and the paper stays descriptive.
9. **Cost.** Negligible (label-only computation).
10. **Effect on contribution.** Converts an identity into a testable, model-free prediction: a
    genuinely new, falsifiable result.
11. **Verification.** Pre-specified tests P1, P2 and P5.
12. **Objection addressed.** "Elementary theory, post-hoc explanation."

## U2. Training-conditional (PAC) novelty-Mondrian thresholds (R04)

1. **Deficiency.** With few novel calibration rows, MCP coverage varies widely across splits
   (solar_flare SD 0.07); a single deployment can be badly under-covered.
2. **Evidence.** v1 verification run.
3. **Improvement.** For each Mondrian group of size n_k, use the r-th smallest score, with r the
   smallest rank such that P{Beta(r, n_k − r + 1) < 1 − α} ≤ δ (Vovk 2012), and +∞ if no rank
   qualifies. δ = 0.1.
4. **Hypothesis.** PAC-MCP lowers the fraction of splits with novel coverage below 1 − α − 0.03,
   at a moderate set-size cost.
5–6. Implemented in `conformal.pac_threshold`; evaluated in U4.
7. **Expected.** Fewer bad splits; larger sets, mostly where n_k is small.
8. **If false.** Report it; the recommendation stays plain MCP.
9. **Cost.** Negligible.
10. Strengthens the remedy's practical reliability (the method is standard, so it is presented as such).
11. **Verification.** P4.
12. **Objection addressed.** "Your guarantee holds only on average."

## U3. Near-duplicate (jittered-copy) injection (R05, R08)

1. **Deficiency.** Only exact duplicates are studied; the exact-key taxonomy cannot see perturbed copies.
2. **Evidence.** Methods §4.1; exploratory distance analysis.
3. **Improvement.** A controlled experiment that measures coverage on **truly new records**,
   defined by ground-truth record identity from the injection. The remedies (exact-key MCP,
   distance-Mondrian, oracle record-identity Mondrian) are compared as jitter grows.
4. **Hypothesis.** The shortfall persists for small jitter (the model still memorizes). Exact-key
   MCP stops helping as soon as copies are perturbed; distance-Mondrian recovers part of the
   shortfall.
5. `experiments.run_neardup`.
6. 37 duplicate-free datasets of the v1 injection experiment; ρ = 0.5; jitter σ ∈ {0, 10⁻³, 10⁻²,
   10⁻¹} × feature SD on numeric features of the copies; RF and LightGBM; 3 seeds; LAC or |res|; α = 0.1.
7. **Expected.** The gap decays with σ; exact-key MCP equals SCP for σ > 0; DCP is in between.
8. **If false.** For example, if DCP does not help, report that near-duplicates require record
   identifiers, which is a limitation of any key-based audit.
9. **Cost.** ≈ 1 h on 4 cores.
10. Defines the boundary of the remedy honestly.
11. **Verification.** Pre-specified descriptive endpoints N1–N3.
12. **Objection addressed.** "Exact duplicates are a special case."

## U4. Prospective validation on unseen suites (R06, R04, R14)

1. **Deficiency.** The explanations were developed on the same 108 datasets.
3. **Improvement.** New datasets from the OpenML AutoML Benchmark (studies 271, 269) and the
   Grinsztajn et al. suites (334–337), minus every dataset already used. They are selected by a
   label-free audit rule **before any model is run**.
6. **Experiment.** 20 seeds; RF, LightGBM, LR/ridge; LAC or |res|; α = 0.1. Methods: SCP, MCP,
   PAC-MCP, DCP, plus the normalized score for regression.
7–8. Pre-specified tests P1–P5 (revised protocol). All results are reported whatever their sign.
9. **Cost.** ≈ 1–2 h.
11. P1–P5.
12. **Objections addressed.** Circularity, baseline completeness, classification analogue of the
    adaptive-score finding.

## U5. Integrity corrections (R10, R11, R16)

Correct the false "no errors" statement; make group-split infeasibility explicit; re-run one new
dataset from a fresh clone; restate what the seed-level CIs mean.

## Not pursued (and why)

* **A new conformal algorithm.** Nothing in the evidence calls for one; the remedies that work
  already exist. Inventing one would add complexity, not science.
* **Full conditional calibration (Gibbs et al. 2025) with a continuous function class.** It
  needs one LP per test point (≈ 10⁸ LP solves here). For the disjoint seen/novel groups it
  reduces to Mondrian. Discussed, not run.
* **Changing the research topic.** The novelty stress test (`audit/novelty_reassessment.md`)
  finds the core question unpreempted. The contribution is narrow but defensible once U1
  succeeds. If U1 fails, the outcome is decision B or C, not a disguised paper.
