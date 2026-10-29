# Second adversarial review (revised manuscript, v2)

Ten passes by role-separated instances of one AI system (not independent human reviewers). Each pass
read the built manuscript `manuscript/build/manuscript_v2.md` against the result files. Findings
marked FIXED were changed in commit `59b5ce9` or earlier; the rest are accepted as stated limitations.

| Pass | Role | Finding | Severity | Outcome |
|---|---|---|---|---|
| 1 | Desk editor | Contribution could look like "Mondrian CP applied to duplicates". Application framing and a model-free predictor make the contribution practical; novelty is modest but defensible for an applied venue. | Moderate | Accepted; framed honestly in Section 2 ("What is new is which groups…") |
| 2 | Hostile statistician | Section 5 listed the "safe" defect sets but omitted kc2, where the check predicted −1.4 pp and new modules were covered at 86.7%. Selective reporting. | **Major** | FIXED: kc2 reported as a miss; exposure (30%) flags it under the combined rule |
| 3 | Hostile statistician | Introduction claimed "where the check raises a flag, the shortfall is real". kc3, airlines, compas and sf-police were false alarms. | **Major** | FIXED: "often real and sometimes large… false alarms cost almost nothing" |
| 4 | Pre-registration auditor | "Two [tests] failed" miscounts: P1 failed, P4 not significant after Holm, P5 not established. | Moderate | FIXED: "Two were clearly supported and three were not" |
| 5 | Pre-registration auditor | Is the "safe" rule in Section 7.1 post hoc? Checked: the rule is in `08_discussion.md`, committed in `aafc419` at 13:42 UTC; the first fresh result file was written at 14:24 UTC. | — | Verified; the claim "before these results existed" is true |
| 6 | Methods reviewer | Fresh-set subsampling rule (uniform rows when a group > 6,000) missing from Methods. | Minor | FIXED (Section 4) |
| 7 | Methods reviewer | "37 benchmark sets without any repeated rows" is wrong: 50 such sets, 37 of them with ≥ 1,000 rows. | Minor | FIXED |
| 8 | Copy editor | Double negatives ("fell −27.5 pp below target"), mixed 0.73 vs 73% formats, "−0.0", figure order (Fig. 5 before Fig. 4), captions naming "bars" for tick marks. | Minor | FIXED |
| 9 | Reference checker | 14 listed references not cited. 11 placed where they fit (software, data source, applications, related Mondrian work, shift-aware CP, time splits); 3 no longer relevant removed (Friedman, Guo, Naeini). Converter check: 0 uncited, 0 unmatched. | Minor | FIXED |
| 10 | Area editor | Does the paper overclaim the predictor? The abstract and Section 8.3 now say it works as a limit and a screen but does not rank data sets; the one linear-model miss (black_friday) is reported. | — | Accepted |

## Residual weaknesses a real reviewer may still raise

1. The predicted gap (Eq. 3) failed the pre-specified rank test on fresh data. The paper reports this
   and narrows the claim, but a reviewer may regard the predictor as weaker than the title of
   Section 3.3 suggests.
2. Random forests were *conservative* on several highly exposed classification sets (airlines +8.7
   pp, KDD Cup'99). The tie explanation is plausible but not separately tested.
3. Twenty fresh data sets, most with low exposure, give limited power; only one fresh data set
   (analcatdata_supreme) shows a large shortfall.
4. Exact-match keys only; near-copies need the distance-based variant.
5. AI-assisted authorship may draw editorial scrutiny; the declaration is kept.
