# Final consistency and reproducibility audit (v2)

## Numbers
* Every number in the revised manuscript that comes from an experiment is a `{{placeholder}}` filled
  by `manuscript/numbers_v2.py` from `results/`. The build aborts on an unresolved placeholder.
  The values used are archived in `manuscript/build/numbers_used_v2.json`.
* Hard-coded numbers were listed automatically and checked one by one. They are design constants
  (splits, tree counts, α, noise levels), plus:
  * 37 injection data sets: 37 files in `results/inject/`; 50 clean data sets, 37 with ≥ 1,000 rows.
  * solar_flare 200-split check: 90.9% (CI 89.9–91.8%) vs 78%, from `results/verification/solar_flare_200splits.json`.
  * kc2 522 rows (`case_studies.csv`), phishing 30 features (`T1_audit.csv`), Deng 690 data sets (literature matrix).
  One error was found ("37 benchmark sets without any repeated rows") and corrected.
* References: all 50 entries cited; no citation without an entry (citation converter check).
* Abstract: 236 words (journal limit 250).

## Reproducibility
* Unit tests: 15/15 pass (`code/tests`).
* Fresh-clone determinism (R11): the repository was cloned into a new directory, and the
  prospective analysis for yeast (OpenML 181) was re-run. Result: 240/240 rows, maximum absolute
  numeric difference 0.0 (runtime column excluded).
* Earlier determinism check (v1) on one main-grid data set: identical.
* Data are fetched from OpenML. Five fresh-set downloads failed for server-side reasons (see the
  protocol, Deviation 2). A later re-run may include them if OpenML serves them correctly. The
  selection file in `results/reinforcement/` records the set actually used.

## Protocol adherence (reinforcement cycle)
* The plan was frozen in commit `91ac5f6`, before any reinforcement data were downloaded.
* Deviations (all recorded in `reinforcement/research_design/revised_experimental_protocol.md`):
  * Amendment 1 (UCI contingency) was not triggered.
  * Deviation 2 consists of four items, all fixed before any outcome was computed:
    * a parsing fix;
    * within-pool de-duplication;
    * a retry rule for transient download failures;
    * an early start of the fresh runs.
* All five pre-specified tests are reported, including the three not supported.

## Original package preserved
* v1 manuscript files (`manuscript/Final_Manuscript*.docx/pdf`, `sections/`, `sections_pr/`) are
  unchanged.
* v1 state: commit `bb7afa9`; local tag `v1-original-submission` (pushing the tag was refused by the
  remote, so the commit hash is the durable reference).
* v2 lives in `manuscript/sections_v2/`, with outputs `Revised_Manuscript.*`, `Revised_Cover_Letter.docx`,
  `Revised_Title_Page.docx` and `supplementary/Supplementary_Material_v2.*`.
