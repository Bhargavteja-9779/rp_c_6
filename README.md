# Duplicate Data Rows Make Prediction Uncertainty Look Better Than It Is: A Simple Check and Fix for New Cases

Research project and submission package. **Current version: final LaTeX manuscript in `paper/` (Springer Nature template); submission package in `submission/`.**
**Target journal: *Journal of King Saud University – Computer and Information Sciences*** (median
67 days from submission to acceptance; 57% of its papers are accepted within 72 days).

Produced with an AI research agent under human direction. The AI use is declared in the manuscript.
The review passes in this repository were role-separated passes of one AI system, not independent
human review.

## The idea in three sentences

Conformal prediction promises, say, 90% coverage, and teams check this on a random test split. If the
data contain repeated rows, many test rows have a copy in the training data, so the check can report
90% while genuinely new cases are covered far less often. The routine we propose has three steps:
* **check:** predict the risk from the data alone, before training;
* **fix:** calibrate seen and new cases separately;
* **report:** give coverage on new cases next to the usual figure.

## Main findings (v2)

* **Applications.** In the NASA mc1 software-defect data, a random forest's 90% sets reported 91.7%
  coverage but covered 62.7% of new modules; after the fix, 90.3%. Phishing and KDD Cup'99 intrusion
  data show similar, smaller shortfalls.
* **Benchmarks (103 OpenML data sets).** The typical data set is not affected; the pre-specified
  primary hypothesis was not supported. Shortfalls are concentrated in data with many label-pure
  repeats.
* **Fresh validation (20 unseen data sets, time-stamped plan).**
  * The fix kept new-case coverage on target.
  * The model-free predicted gap held as a limit (20/20 data sets) and worked as a screen.
  * It did **not** rank data sets by severity, and the rank test failed.
  * All five pre-specified tests are reported.
* **Near-copies.** Exact matching cannot see slightly perturbed copies. Calibration by distance to
  the training rows still keeps coverage on target.

## Where things are

| Folder | Content |
|---|---|
| `submission/` | **`DuplicateRowsCoverage_Submission.zip`**: manuscript PDF, supplement PDF, cover letter (DOCX/PDF), Word version, tested LaTeX source zip, title page, README with author actions |
| `paper/` | LaTeX sources (`main.tex`, `supplement.tex`, `sections/`), generated `tables/macros.tex` (every number) and `tab_*.tex`, `figures/`, `build.sh` (build + layout checks), `make_docx.py`, `make_cover_letter.py` |
| `tool/` | **covercheck**: installable check-fix-report tool (CLI + Python API + HTML report, 11 tests) |
| `code/visualization/` | One script per figure (PDF + PNG, 8 pt, journal widths, 95% intervals) |
| `review/` | Simulated review rounds 12-14 (final), `claim_evidence_matrix.md`, `final_audit.md` |
| `research_design/` | Hypothesis register (H1-H9) appended to `experimental_protocol.md`, `deviations.md` (D1-D17), `data_leakage_audit.md` with planted-leak test |
| `manuscript/` | **v2:** `Revised_Manuscript.docx/.pdf`, `Revised_Cover_Letter.docx`, `Revised_Title_Page.docx`, sources in `sections_v2/`, build with `python build_manuscript.py v2`. **v1 (preserved, unchanged):** `Final_Manuscript*.docx/.pdf`, `sections/`, `sections_pr/` |
| `supplementary/` | v2: `Supplementary_Material_v2.docx/.pdf`; v1: `Online_Resource_1.*` |
| `reinforcement/` | Reinforcement cycle: integrity audit, risk register (R01–R18, with resolutions), journal-fit assessment, revised protocol and deviations, second adversarial review, consistency audit, **`submission_readiness_report.md`** |
| `code/` | Pipeline (`run_all.py`, stages main/inject/capacity/external/normalized/neardup/prospective/analyze), tests (15), experiment scripts |
| `results/` | Raw per-split results, tables, statistics, figures; `results/reinforcement/` holds the v2 analyses |
| `research_design/`, `literature_review/`, `journal_selection/`, `review/` | v1 design, literature, journal analysis and review trail |

Rebuild everything: `python code/run_all.py --mode full` (stages main ... analyze, amendment2, posthoc, paper).

The v1 state is commit `bb7afa9` (local tag `v1-original-submission`).

## Status

**Decision A: scientifically reinforced, ready for submission**
(`reinforcement/submission_readiness_report.md`). What remains is author-only:
* names and affiliations;
* competing interests and funding;
* a Zenodo DOI for the code;
* confirming the AI-use statement against the journal's policy.

Acceptance cannot be guaranteed at any journal.
