# Submission readiness report (reinforcement cycle)

## Final decision: **A. Scientifically reinforced — ready for submission**

Remaining actions belong to the author only: author list, affiliations, competing interests and
funding, a Zenodo DOI for the code, and confirming the AI-use wording.

**Why A and not B.**
* The central contribution is defensible: a practical check–fix–report routine for a failure of
  conformal coverage on new cases, together with a model-free predictor that works as a limit and as
  a screen.
* Every planned experiment was executed, including those that failed.
* Claims were narrowed to match the evidence, most importantly that the predictor does not rank data
  sets.
* Reproducibility checks pass: 15 unit tests, a bit-identical fresh-clone re-run, and every number
  built from result files.
* No critical item is open in the risk register (R01–R18).

## Target journal
**Journal of King Saud University – Computer and Information Sciences** (Springer Nature, Q1 JCR).
* Crossref analysis: median submission-to-acceptance 67 days (95% CI 65–69, n = 647), with 56.9%
  of papers accepted within 72 days.
* The 72-day limit is therefore likely but **not guaranteed**: about 43% of its papers take longer.
* Pattern Recognition (about 250 days) is kept only as a non-compliant alternative.

## What changed from v1
| Area | v1 | v2 |
|---|---|---|
| Title | "Seen or new? Duplicate records, conformal coverage on novel inputs, and a novelty-conditional remedy for tabular benchmarks" | "Duplicate Data Rows Make Prediction Uncertainty Look Better Than It Is: A Simple Check and Fix for New Cases" |
| Framing | Benchmark-methodology study | Application paper: check, fix, report; software defects, network intrusion, phishing |
| Prose | Technical, hypothesis-labelled (H1–H6) | Plain language; terms like "seen/new cases", "predicted gap" |
| Predictor | Exposure only (needs a model for c_S) | Adds label purity, Eq. (3); needs no model |
| Validation | Same data as development | Plus 20 fresh data sets under a time-stamped plan |
| Near-copies | Exploratory distance bins | Controlled jittered-copy experiment with ground truth |
| Remedies | Mondrian; normalized score | Plus safety margin (training-conditional) and distance-based calibration, evaluated on fresh data |

## Key results (all from `results/`)
* **Applications.**
  * mc1: reported 91.7%, new modules 62.7%, after the fix 90.3%.
  * pc2: reported 91.0%, new modules 62.5%, after the fix 89.4%.
  * KDD Cup'99: new connections 88.6%, after the fix 91.6%.
  * Phishing: new sites 84.8%, after the fix 90.1%.
  * Reported openly: kc2 is a miss of the predicted gap, and kc3 is a false alarm.
* **Benchmarks (103).** No typical shortfall (pre-specified H1 not supported). Shortfalls are
  concentrated in highly exposed, label-pure data.
* **Fresh data (20 data sets).**
  * The fix kept new-case coverage on target: worst data set −0.7 pp for random forests and
    −0.9 pp for LightGBM.
  * The bound held in 20/20 data sets.
  * Screen:
    * no misses for random forests or LightGBM;
    * one miss for linear models (black_friday);
    * purity removed four false alarms raised by exposure alone.
  * The rank test failed (ρ = 0.12, Holm p = 0.31).
  * The safety margin reduced bad splits from 4.2% to 0.5%, but this is not significant after Holm
    correction (p = 0.062).
* **Near-copies.**
  * The exact key detects none of them.
  * The shortfall persists: −4.3 to −2.7 pp for random forests in classification.
  * Distance-based calibration stays on target.

## Residual risks (honest)
1. The novelty of the method is modest (Mondrian CP is standard), and the selling point is
   practicality. An editor wanting methodological novelty may reject the paper.
2. The predictor failed its pre-specified rank test on fresh data. This is disclosed, and the claim
   is narrowed.
3. Only one fresh data set shows a large shortfall, so evidence on fresh data comes mainly from that
   case plus the screen's behaviour.
4. AI-assisted authorship is declared, and some editors may scrutinize it.
5. The 72-day acceptance window is probable (57%), not certain.

## Submission package
| Item | File |
|---|---|
| Manuscript (anonymized) | `manuscript/Revised_Manuscript.docx`, `.pdf` |
| Title page | `manuscript/Revised_Title_Page.docx` (author fields to complete) |
| Cover letter | `manuscript/Revised_Cover_Letter.docx` |
| Supplementary material | `supplementary/Supplementary_Material_v2.docx`, `.pdf` |
| Figures (EPS/TIFF/PNG) | `results/reinforcement/figures/Fig_cases, Fig_inject, Fig_fresh, Fig_neardup` |
| Code and data provenance | repository; one-command rebuild (`code/run_all.py`, `manuscript/build_manuscript.py v2`) |
| Review trail | `reinforcement/audit/`, `reinforcement/review/` |
