# Review 12 (simulated): statistician / conformal-methods reviewer

**Label: simulated review.** This is a role-separated pass by the AI system that produced the paper,
written as a reviewer trying to reject it. It is not an external review.

**Recommendation as written by the simulated reviewer:** major revision, close to reject. The fix is
textbook Mondrian conformal prediction, and the novel predictor fails its own pre-registered ranking
test.

| # | Objection | Severity | Action taken | Status |
|---|---|---|---|---|
| 12.1 | Proposition 2 is asymptotic and rests on idealized assumptions A2/A3; the predicted gap did not rank wave-1 data sets (H6). Is the "check" anything more than exposure? | Major | Claim narrowed throughout to "limit and screen, not forecast". Abstract, Discussion (limitation 2) and Conclusion say so. The ablation (Table 6) shows what purity adds: fewer false alarms at equal sensitivity. Wave 2, which has more real shortfalls, supports ranking (secondary). | Addressed (wording + evidence) |
| 12.2 | The screening result depends on the −2 pp threshold that defines a "real shortfall"; 13 positives give a wide CI. | Major | New sensitivity analysis: the flag rule is kept fixed and the positive threshold is varied (−1, −2, −3 pp). Reported in Supplementary Sect. S11. | Addressed (new analysis) |
| 12.3 | Specificity is only about 60%; a screen that flags half of all data sets is not very informative. | Moderate | Stated in Results (H7). A false alarm costs little, because the fix changes set sizes by a factor of about 1.0 (H4). Exposure alone has more false alarms (Table 6). | Stated as a limitation of the screen |
| 12.4 | Multiplicity across H1–H9 and the many secondary analyses. | Moderate | Holm correction within each pre-registered family. Secondary and post hoc analyses are labelled, and none is used for a primary claim. | Stated |
| 12.5 | Novelty: the fix is standard Mondrian CP, and Eq. (3) is elementary. | Major for a methods venue | The paper says explicitly which parts are standard (Props. 3 and margin) and which are new (Eq. 4, Prop. 2, the check, the evidence, the tool). It is framed as an application/evaluation paper for an applied journal. | Accepted risk; stated honestly |
| 12.6 | The sampling-noise check finds an unexplained excess of bad splits for LightGBM. | Minor | Reported as unexplained (limitation 5). | Stated |
