# Seen or new? Duplicate records and conformal coverage on novel inputs

Research project and submission package. **Primary target: *Pattern Recognition* (Elsevier).**
Fallback: *Journal of King Saud University – Computer and Information Sciences*. Both builds
are included. Produced by an AI research agent; see
"Status" below before using any of it.

## Main findings

* **Theory.** Under a random row split, coverage of split conformal prediction on records with
  no training copy equals (c − π c_S)/(1 − π). Here π is the share of test rows that have an exact
  training copy and c_S is their coverage. If seen rows are always covered, the error rate on new
  records is α/(1 − π). A label-free formula predicts π from duplicate-group sizes. Novelty-Mondrian
  CP is exactly valid for any mix of seen and new records.
* **Benchmarks (103 OpenML-CC18/CTR23 datasets).** The predicted exposure matched the observed
  exposure (MAE 0.0012). The pre-specified primary hypothesis (typical under-coverage) was **not
  supported**: median gaps were −0.8 to +0.5 pp. Shortfalls are concentrated in high-exposure
  datasets whose seen rows are over-covered, with a worst case of −16.9 pp.
* **External data with documented duplication** (NASA MDP mc1/pc2/kc3/mw1, KDD Cup'99). Shortfalls
  reach −27.5 pp. Novelty-Mondrian restores coverage (worst −2.1 pp, no CI below zero).
* **Controlled injection.** Shows a monotone dose–response (RF −12.8 pp at ρ = 1, against a limit
  of −14.8 pp). Within-learner capacity variation showed no detectable effect at benchmark
  exposures (reported as not supported).
* The remedy costs ≤ 4.4% in median set size for novel records, and its computation is negligible.
* In regression, a distance-normalized score (k-NN difficulty) removes most of the shortfall on
  its own (worst −3.4 pp vs −16.9 pp). It is an effective heuristic but carries no guarantee.

## Package map

| Folder | Content |
|---|---|
| `journal_selection/` | Crossref-based submission-to-acceptance analysis of ~40 journals, selected-journal report, guideline checklist, journal-fit audit |
| `literature_review/` | Candidate directions (17), literature matrix (43 entries), research-gap chain, novelty map, DOI verification data |
| `research_design/` | Research questions and hypotheses, theory with proofs, pre-specified protocol (frozen at commit `0e58bdd`), deviations, leakage audit, exploratory pilot |
| `code/` | Pipeline (`run_all.py`), tests, configs, extra experiments; see `code/README.md` |
| `results/` | Raw per-split results, tables, `statistics.json`, figures (PNG/EPS/TIFF), logs |
| `manuscript/` | Pattern Recognition build: `Final_Manuscript_PatternRecognition.docx/.pdf`, `highlights_PatternRecognition.docx`, `cover_letter_PatternRecognition.docx`. JKSU-CIS build: `Final_Manuscript.docx/.pdf`, `cover_letter.docx`. Shared `title_page.docx`, section sources, build scripts (`python build_manuscript.py pr|jksu`), claim–evidence matrix |
| `supplementary/` | Online Resource 1 (DOCX/PDF) |
| `review/` | Ten role-separated adversarial reviews, response ledger, final audit and readiness decision |

## Status

**NOT READY for submission. Only the author's actions remain**
(`review/final_audit.md`):

* Author names, affiliations, declarations, an anonymized repository/DOI, and APC verification
  are placeholders.
* The AI-use statement must be confirmed against the journal's policy.
* The reviews were simulated role passes by one AI system, not independent human review.
* Acceptance cannot be guaranteed at any journal. At Pattern Recognition the main risk is that
  the contribution is judged incremental; see `journal_selection/selected_journal.md` for the
  fallback cascade.
