# Review-response ledger

All ten reviews are role-separated passes by the same AI system, not independent human peer review.

| Reviewer | ID | Severity | Concern | Action | Status |
|---|---|---|---|---|---|
| 01 | R1.1 | MAJOR | The remedy is ordinary Mondrian CP and Propositions 1–3 are elementary (total probability,… | Intro contribution 3 now says explicitly that the method is standard Mondrian CP. The nove… | Fixed (framing); residual risk that an editor still judges it incremental: MODERATE |
| 01 | R1.2 | MAJOR | The pre-specified primary hypothesis failed. Is the phenomenon practically significant at … | Added an external validation on datasets with documented duplication (NASA MDP extras, KDD… | Fixed with new evidence |
| 01 | R1.3 | MINOR | The title promises a remedy, but the remedy's main value is for high-exposure data.… | The title and abstract keep the remedy; the discussion gives a concrete threshold (π̄ ≥ 0.… | Accepted as is |
| 02 | R2.1 | MODERATE | Multivalid / multi-group CP (overlapping groups) is missing from related work.… | Added Bastani et al. (2022) (DOI verified via Crossref) and noted that conditional calibra… | Fixed |
| 02 | R2.2 | MODERATE | The motivating prevalence numbers come from two non-peer-reviewed preprints (Li 2026; Roth… | Marked as preprints in the text and references. Prevalence is now also supported by our ow… | Fixed |
| 02 | R2.3 | MINOR | Full texts of several cited works were not read in this environment (abstract-level eviden… | Recorded in literature_matrix.csv (evidence_basis). Claims about cited works are limited t… | Disclosed; residual risk LOW–MODERATE |
| 03 | R3.1 | MAJOR | The confirmatory set DUP (π̄ ≥ 0.01) mixes datasets with negligible expected gaps with a f… | Acknowledged in the Discussion and Limitations. Exposure-stratified analysis added, labell… | Fixed / disclosed |
| 03 | R3.2 | MODERATE | Spearman p-values for H1a are not corrected for multiplicity.… | Stated in Methods.… | Fixed |
| 03 | R3.3 | MODERATE | Bootstrap CIs of medians from 12 regression datasets are coarse.… | Reported as such. The conclusions do not rest on the regression medians alone.… | Disclosed |
| 03 | R3.4 | MODERATE | MCP-R gap −5.8 pp on solar_flare appeared to contradict Proposition 3.… | Verification with 200 extra splits: 0.909 (95% CI 0.899–0.918). Reported in the Results an… | Fixed |
| 04 | R4.1 | MODERATE | Ties: the upper coverage bound fails with tied scores (k-NN probabilities, duplicate calib… | Lemma/Prop. 1 text states that ties preserve the lower bound only. Results explain the k-N… | Fixed |
| 04 | R4.2 | MINOR | Novelty is defined on raw feature keys, whereas models see preprocessed features (infreque… | Makes the analysis conservative (fewer seen rows). Noted in data_leakage_audit.md.… | Disclosed |
| 04 | R4.3 | MINOR | Equation and code consistency.… | Checked: conformal_quantile implements ⌈(n+1)(1−α)⌉ with +∞ fallback; Mondrian uses per-gr… | Verified |
| 05 | R5.1 | MAJOR | The curated suites under-represent duplicated data (CTR23 excludes datasets needing groupe… | External validation set added (see R1.2).… | Fixed with new evidence |
| 05 | R5.2 | MODERATE | KDD Cup'99 required uniform row subsampling, which departs from the group-preserving rule.… | Pre-specified and disclosed. Uniform subsampling keeps very large duplicate groups heavily… | Disclosed |
| 05 | R5.3 | MODERATE | Legitimate recurrence vs duplicate records: is the novel-row estimand right?… | Estimand discussion in Theory and Recommendations (choose the estimand deliberately).… | Addressed |
| 06 | R6.1 | MODERATE | No stronger conditional-coverage baseline (e.g. Gibbs et al. 2025).… | For the two disjoint groups considered, conditional calibration over group indicators redu… | Addressed by argument |
| 06 | R6.2 | MINOR | Untuned learners.… | Fixed defaults pre-specified; capacity explicitly varied; disclosed in Limitations.… | Disclosed |
| 07 | R7.1 | MODERATE | Pre-registered Experiment G (computational cost) had not been run.… | Run: hashing ≤ 0.17 s, audit ≤ 8 ms, MCP thresholds ≈ 40 µs vs LightGBM fit 0.6–2.8 s on 3… | Fixed |
| 07 | R7.2 | MINOR | The practical threshold π̄ ≥ 0.1 is post hoc.… | Labelled as derived from our data.… | Disclosed |
| 08 | R8.1 | MAJOR | Alternative explanation: novel records in naturally duplicated data are rarer and harder, … | The injection experiment duplicates uniformly random rows, so seen and novel rows share a … | Addressed with existing evidence |
| 08 | R8.2 | MODERATE | k-NN/LAC and KDD over-coverage could hide under-coverage in other places.… | Tie mechanism explained; per-family reporting keeps them separate; the abstract range excl… | Fixed |
| 09 | R9.1 | MAJOR | Figure numbering out of order (Fig. 8 cited before Fig. 4); Fig. 3 produced but never cite… | Renumbered: mechanism figure is now Fig. 3, the learner strip plot moved to the supplement… | Fixed |
| 09 | R9.2 | MODERATE | Scope fit for JKSU-CIS (mostly applied DL papers).… | The cover letter and introduction emphasize reliable ML evaluation and data quality for pr… | Addressed; residual risk MODERATE |
| 09 | R9.3 | MODERATE | Double-anonymous review: the repository link and AI-use statement must not reveal identity… | Placeholders instruct the author to provide an anonymized repository; the title page is se… | Author action required |
| 10 | R10.1 | MAJOR (not fatal) | The central claim could be judged weak because the primary test failed.… | The paper's claims are now proportional: the mechanism (exact), the predictability (exposu… | Fixed |
| 10 | R10.2 | MODERATE | 'Pre-registered' implies an external registry.… | Reworded to 'pre-specified protocol committed to version control (not an external registry… | Fixed |
| 10 | R10.3 | MODERATE | Over-generalization: 'datasets with conflicting labels are unaffected' rests on one datase… | Narrowed to 'a dataset (cps88wages)'.… | Fixed |
| 10 | R10.4 | MODERATE | Discussion claimed '5–17 points' for the NASA defect data, but kc1 shows 3–7.… | Replaced with exact, sourced figures (suites: up to 16.9 pp on solar_flare; external: up t… | Fixed |
| 10 | R10.5 | MINOR | Capacity half of H5 not supported.… | Reported as not supported, with explanation (underpowered at moderate exposure; k-NN ties)… | Disclosed |
| 11 | R11.1 | MAJOR | Would a locally adaptive (normalized) score already remove the gap?… | New pre-specified baseline: yes, largely in regression (worst −3.4 pp); reported; Mondrian kept as the guaranteed option… | Fixed with new evidence (claim weakened, stated) |
| 11 | R11.2 | MAJOR | Novelty bar of Pattern Recognition… | Framed as characterization + evaluation finding; cascade plan… | Residual risk HIGH |
| 11 | R11.3 | MODERATE | Elsevier formatting… | Numbered refs, highlights, bios, AI declaration, 31 pages… | Fixed |
| 11 | R11.4 | MODERATE | Cite the journal's related work… | Three 2026 Pattern Recognition papers added (title-level)… | Fixed |
