# Project integrity report (Phase 1, reinforcement cycle)

Date: 2026-10-21. Baseline preserved as commit `bb7afa9` on branch `claude/hopeful-thompson-8gd034`
and as local tag `v1-original-submission`. Pushing the tag was refused by the remote (HTTP 403;
only the designated branch may be pushed), so the commit hash is the durable reference.

Every status below comes from a check executed in this cycle. Nothing is taken from earlier
reports.

| Component | Artifacts | Verification method | Status | Deficiencies found | Importance | Action |
|---|---|---|---|---|---|---|
| Unit tests | `code/tests/test_core.py` (11 tests) | `pytest` run | **VERIFIED** (11 passed) | Tests cover conformal mechanics, exposure formula, splits, ECE. No test covers the experiment drivers end to end | Medium | Add driver smoke tests for the new code |
| Main grid raw results | 103 × {main, calib, dist, audit} files in `results/raw/` | Row counts, error column, seed and model coverage per file | **VERIFIED** | 103,400 rows, 0 error rows, 10 seeds and 5 learners everywhere. Distance analysis absent for 2 datasets (nomao, connect-4: cost cap, documented) | High | None |
| Injection experiment | 37 files | Error column, row counts | **VERIFIED** (7,400 rows, 0 errors) | — | High | None |
| Capacity experiment | 29 files | Same | **VERIFIED** (3,190 rows, 0 errors) | — | Medium | None |
| External validation | 5 datasets × 4 files | Same | **PARTIALLY VERIFIED** | **20 failed fits not reported earlier**: KDD Cup'99, group-split protocol, 4 of 10 seeds. One duplicate group holds 11,573 of 30,000 rows (38.6%), so whole-group splitting leaves an empty partition. The protocol-R results used in the paper are complete | Medium (G protocol not used for external claims), but the earlier "no errors" statement in `review/final_audit.md` was **false** | Correct the audit statement; document the infeasibility of the group split for dominant groups |
| Normalized-score baseline | 12 files | Same | **VERIFIED** (480 rows, 0 errors) | Regression only, 2 learners | High (changes the interpretation of the remedy) | Extend in the reinforcement experiments |
| Statistics | `results/statistics.json`, tables | Re-ran `analysis.run` and compared byte for byte | **VERIFIED** (byte-identical) | — | High | None |
| Determinism of experiments | One dataset re-run in a fresh clone (previous cycle) | Bit-identical comparison | **PARTIALLY VERIFIED** (1 of 108 datasets) | Full regeneration not repeated (≈ 5 h × 4 cores) | Medium | Repeat for one new-experiment dataset |
| Protocol freeze | `research_design/experimental_protocol.md`, commit `0e58bdd` (2026-10-20 17:33 UTC) | `git log`: the first results commit is `5383ede` (2026-10-21 01:39) | **VERIFIED** (freeze precedes results) | Freeze is a self-controlled git commit, not an external registry | Medium | Disclosed |
| Theory | `research_design/theory.md`, manuscript §3 | Re-derived Propositions 1–3 by hand; unit tests reproduce Prop. 1 and 2 numerically | **VERIFIED** | Propositions are correct but elementary. Prop. 1 is an identity plus bounds; Prop. 3 is the standard Mondrian argument | **High** (novelty) | Reinforce with a non-trivial, testable result (see the reinforcement plan) |
| Literature and DOIs | `literature_review/*`, Crossref JSON | DOIs resolved via Crossref/DataCite | **PARTIALLY VERIFIED** | Full texts of most works were not read; 3 Pattern Recognition papers cited from titles only. New close prior art found in this cycle (Deng 2026, arXiv:2609.29580; Tareaf et al. 2026, arXiv:2609.11838) is **missing** from the manuscript | High | Update the literature and novelty argument |
| Journal selection | `journal_selection/*` | Re-ran the Crossref timeline for JKSU-CIS; searched for official Pattern Recognition timeline data | **VERIFIED for JKSU-CIS** (median 67 d, n = 647, published since Apr 2026). **FAILED for Pattern Recognition** under the 72-day constraint (ScienceDirect Insights: ≈ 250 days submission→acceptance) | The previous cycle moved to Pattern Recognition after the user waived the timeline; Master Prompt 2 reinstates it | High | Re-decide (see journal_fit_assessment.md) |
| Manuscript builds | `Final_Manuscript{,_PatternRecognition}.{docx,pdf}` | Rebuilt; placeholder check; citation cross-check; abstract word count | **VERIFIED** (builds; 0 unresolved placeholders; all citations resolve) | Claims inherit the scientific weaknesses below | High | Reconstruct after new evidence |
| Figures and tables | `results/figures/*`, `results/tables/*` | Generated from tables by code | **VERIFIED** | — | Medium | Regenerate after new analyses |
| Supplement | `supplementary/Online_Resource_1.{docx,pdf}` | Rebuilt | **VERIFIED** | — | Low | Update |
| Previous reviews | `review/*.md` | Read | **VERIFIED as existing**; they are single-system role passes, not independent review | Some conclusions were optimistic (e.g. "no errors", "no fatal flaw") | Medium | Superseded by this cycle |
| Predictions | Not stored (only per-split metrics) | — | **NOT AVAILABLE** | Score-level re-analysis (e.g. PAC thresholds) needs refits | Medium | New experiments store what they need |
| Cover letters, title page, highlights | DOCX files | Opened via python-docx in the previous cycle | **VERIFIED** | Author placeholders (intended) | Low | Regenerate |
