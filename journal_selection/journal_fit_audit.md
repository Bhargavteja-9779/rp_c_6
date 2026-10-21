# Journal-scope and contribution-fit audit (Agent 1 + Associate-Editor simulation)

**Target:** Journal of King Saud University – Computer and Information Sciences (Springer Nature).
**Limitation:** recent JKSU-CIS articles were identified and their metadata verified through the
Crossref API. Their full texts could not be retrieved from this environment, so the comparison
below rests on titles and metadata. The methodological depth of these papers was not verified.

## Recent relevant publications in the target journal (Crossref-verified metadata)

| Year | Title | DOI | Relation to this manuscript |
|---|---|---|---|
| 2025 | Conformal deep forest for uncertainty-aware classification | 10.1007/s44443-025-00175-3 | Conformal prediction for classification: shows the topic is in scope |
| 2026 | HF-DIF: Hierarchical feature-selected deep isolation forest for unsupervised anomaly detection on tabular data | 10.1007/s44443-026-00706-6 | Tabular ML methodology |
| 2025 | Robust representation of domain incomplete tabular data via cross-modal debiasing and prototype-fused reconstruction | 10.1007/s44443-025-00225-w | Tabular data quality |
| 2024 | Representing uncertainty and imprecision in machine learning: a survey on belief functions | 10.1016/j.jksuci.2023.101904 | Uncertainty in ML |
| 2026 | Efficient uncertainty quantification for power allocation in wireless networks | 10.1007/s44443-026-00465-4 | Applied uncertainty quantification |
| 2024 | Machine learning-based ransomware classification of Bitcoin transactions | 10.1016/j.jksuci.2024.101925 | Applied ML evaluation |

## Journal-fit matrix

| Editorial requirement | Evidence in the manuscript | Status | Required correction |
|---|---|---|---|
| Scope alignment | Reliable ML evaluation, uncertainty quantification and data quality; journal covers "all aspects of both foundations of computer and its practical applications" | Pass | — |
| Novelty threshold | Novelty map; the paper claims the finding, exact decomposition, exposure formula, admissibility argument and evidence, not a new algorithm | Pass (moderate risk) | Keep the framing honest; do not over-claim |
| Scientific significance | External data with documented duplication shows 17–27 pp shortfalls; benchmark-wide effect is small | Pass | — |
| Methodological rigor | Pre-specified protocol, proofs, unit tests, seed-level CIs, Holm correction, null control | Pass | — |
| Experimental depth | 103 + 5 datasets, 5 learners, 4 scores, 3 α, 2 protocols, injection, capacity, near-duplicates, cost | Pass | — |
| Baseline quality | Split CP (standard), group split, CQR (adaptive), distance-Mondrian; conditional calibration reduces to Mondrian for disjoint groups | Pass | — |
| Statistical validity | Dataset as unit; Wilcoxon/Holm; bootstrap; failure of the primary hypothesis reported | Pass | — |
| Reproducibility | Single entry point; raw results archived; tests; documented environment | Pass (author must deposit and anonymize the repository) | Author action |
| Writing and presentation | Built DOCX (native Word equations) + PDF; figures as EPS/TIFF at 600 dpi | Pass | Author proofreading |
| Journal compliance | Abstract 150–250 words; 6 keywords; declarations; double-anonymous manuscript; author–year references | Pass with author placeholders | Author must complete the title page and declarations |

## Desk-rejection simulation (Associate Editor)

1. *Appropriate for the audience?* Yes. ML-evaluation reliability is a computer-science concern and the paper includes practical recommendations.
2. *Contribution substantial?* Borderline to adequate. The theory is elementary, but the quantification across 108 datasets, the causal injection evidence and the external validation make it more than routine.
3. *More than a routine application?* Yes: it reports a failure mode of a widely used method, with its mechanism.
4. *Genuine gap?* Yes; no prior UQ-focused duplicate study was found (searches documented).
5. *Evidence strong enough for the claims?* Yes, after the claims were narrowed (primary hypothesis reported as not supported).
6. *Methods and baselines appropriate?* Yes.
7. *Compares with the most relevant prior work?* Yes (Li 2026; Roth 2026; Mondrian / conditional CP literature).
8. *Expected depth?* Yes.
9. *Conclusions proportionate?* Yes, after Review 10 corrections.
10. *Obvious reason for desk rejection?* None found among the fixable items. Remaining risks: perceived incrementality; reviewers unfamiliar with conformal prediction; reliance on two preprints for motivation.
