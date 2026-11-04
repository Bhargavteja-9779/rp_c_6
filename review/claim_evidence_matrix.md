# Claim–evidence matrix (final manuscript, `paper/main.tex`)

Every claim in the abstract, introduction and conclusion is listed with:
* its type: **proven** (theory), **empirical-pre** (pre-specified test), **empirical** (pre-specified
  descriptive analysis) or **post hoc** (added after results were seen);
* the result file and the macro behind the number;
* its status.

Claims without evidence were removed or softened, as noted.

| # | Claim (where) | Type | Evidence: file → macro | Status |
|---|---|---|---|---|
| 1 | On mc1, RF sets report 91.7% coverage but cover 62.7% of new modules; 90.3% with the fix (Abstract, Intro, Concl.) | empirical | `results/reinforcement/tables/case_studies.csv` → `\NCsMcOneReported`, `\NCsMcOneNew`, `\NCsMcOneFixed` | Supported |
| 2 | 37% of new mc1 modules receive an empty set (Intro) | empirical (tool demo) | `results/reinforcement/tables/tool_mc1.csv` → `\NToolStdEmpty` | Supported |
| 3 | Tested on 12 application, 103 benchmark and 47 fresh data sets (Abstract, Intro) | descriptive | `case_studies.csv`, `results/statistics.json`, selection JSONs → `\NCsNFlagTotal`, `\NNTotal`, `\NScpN` | Supported |
| 4 | The check flagged all 13 fresh data sets with a real shortfall; 95% CI for sensitivity 75–100% (Abstract, Concl.) | empirical-pre (W1, `b5bbd25`) | `results/reinforcement/statistics_amendment2.json` → `\NScpPos`, `\NScpSensCi` | Supported. Pooling waves 1 and 2 is reported; the primary pre-specified test was wave 2 alone (9/9, Holm p = 0.002) |
| 5 | With the fix, new-case coverage never fell more than 2.5 pp below target on any fresh data set (Abstract, Concl.) | empirical-pre (P3/W2) | `statistics_reinforcement.json` (P3), `statistics_amendment2.json` (W2) → `\NWTwoWorstFixAbs` | Supported. **Softened** from "within 2.5 points of target", because full-set fallbacks over-cover |
| 6 | The check is a limit and a screen, not a forecast; it did not rank wave-1 data sets (Abstract, Concl.) | empirical-pre (P1) | `statistics_reinforcement.json` → `\NPrRfRho`, `\NPrHolmPOne` | Supported (negative result stated) |
| 7 | Exact matching misses near-copies; distance calibration handles them (Abstract, Concl.) | empirical (near-copy experiment) + post hoc (planted leak) | `tables/neardup_summary.csv`, `results/e10_planted_leak/planted_leak.json` → `\NNdCla*`, `\NLeakJitterRecall` | Supported |
| 8 | The closed form of the label-pure share (Eq. 4) and the shortfall formula (Eq. 5) are new to our knowledge (Intro) | proven + novelty claim | Proofs in Supplement S1; literature review (Table 1) | Proven. Novelty is hedged ("to our knowledge"), not "state of the art" |
| 9 | Separate calibration is standard Mondrian CP (Intro) | proven (standard) | Prop. 3 with proof; cited | Stated as standard |
| 10 | The tool reproduced the pipeline on 20 freshly downloaded files (Intro) | post hoc | `results/e14_tool_validation/tool_validation.json` → `\NTvN`, `\NTvFixTwoSe`, `\NTvFlag` | Supported; labelled post hoc |
| 11 | Most standard benchmarks are not affected, and the check says so (Concl.) | empirical-pre (H1, negative) | `results/statistics.json` → `\NHOneMinPHolm`; strata `X2_exposure_strata.csv` | Supported |
| 12 | The fix costs almost nothing (Concl.) | empirical-pre (H3/H4) + post hoc cost | `results/tables/T2_main_alpha0.1.csv` (size ratios), `results/e13_cost/cost.json` → `\NHThreeNovelRatioRange`, `\NCostCalExactMax` | Supported |
| 13 | Negative results are reported with the positive ones (Intro) | process | H1, H6 (wave 1), H8 and H9 all reported in Table 3 and Sect. 6.2 | Supported |
| 14 | Evidence comes from random splits of public data, not a deployed system (Concl.) | limitation | — | Stated |
| 15 | New defective mc1 modules are not covered without class-wise calibration (Results, Limitations) | post hoc | `results/e12_qualitative/class_conditional.json` → `\NCcFixDefCov`, `\NCcClsDefCov` | Supported; labelled post hoc |

Removed or softened during the final review:
* "within 2.5 points of the target" became "never more than 2.5 points below" (claim 5).
* "most likely because of tied scores" was removed after test W5 refuted it (D16).
* "the shortfall is real" on every flag became "often real, sometimes large; false alarms are cheap".
