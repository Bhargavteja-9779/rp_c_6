# Review 14 (simulated): reproducibility and research-integrity reviewer

**Label: simulated review.** This is a role-separated pass by the AI system, not an external review.

**Recommendation as written by the simulated reviewer:** minor-to-major revision. The record keeping
is unusually complete, but the number of amendments invites forking-path concerns.

| # | Objection | Severity | Action taken | Status |
|---|---|---|---|---|
| 14.1 | Seventeen deviations and many post hoc analyses: a garden of forking paths. | Major | Every deviation is dated and listed (Supplementary Sect. S3). The primary tests of each plan are reported unchanged, including the failures (H1, H6 wave 1, H8, H9). Post hoc analyses are labelled in the text and never carry a primary claim. | Stated / mitigated |
| 14.2 | Some explanations were changed after testing (tied scores replaced by the seen-row under-coverage explanation, D16). | Moderate | The paper says so explicitly (Sect. 6.2): the pre-specified test refuted the first explanation. | Addressed |
| 14.3 | Reproducibility depends on OpenML and UCI servers; downloads failed during the study. | Moderate | Selection files and logs are committed; per-split results are archived; the data cache can be archived with the code. Authors must deposit the repository and cache (Zenodo) at submission. | Author action |
| 14.4 | AI-generated research: accountability and verification. | Moderate | AI use is declared in the Methods and the Acknowledgements; the authors must check and approve the work. | Author action |
| 14.5 | Are numbers in text, tables and figures consistent? | — | All numbers come from generated macros. The build fails on unresolved placeholders. A fresh-clone re-run reproduced a data set bit for bit. | Verified |
| 14.6 | Fixed-rule examples could still be cherry-picked through the choice of rule. | Minor | The rule is stated in the caption, includes outcome-independent picks ((a), (b)), and deliberately includes failure cases ((c), (d)). | Addressed |
