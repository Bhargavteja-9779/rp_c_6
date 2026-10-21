# Claim-to-evidence matrix (Phase 15)

Numbers in the manuscript are inserted by `numbers_from_results.py`, so each one traces to
`results/statistics.json` or `results/tables/*.csv`. `build/numbers_used.json` records every
inserted value.

| # | Manuscript claim | Type | Evidence (file → key) | Classification | Decision |
|---|---|---|---|---|---|
| 1 | Coverage on novel records equals (c − π c_S)/(1 − π); memorization limit α/(1 − π) | Theoretical | Proposition 1 proof (03_theory.md); unit test `test_mondrian_group_validity_and_marginal_failure` | Directly supported (proof) | Keep |
| 2 | Exposure is predictable from group sizes (Prop. 2) | Theoretical + empirical | Proof; `test_expected_exposure_matches_simulation`; statistics.json → rq1.pred_vs_obs_exposure_mae = 0.0012, r = 0.9998 | Directly supported | Keep |
| 3 | Novelty-Mondrian CP valid for each group and any deployment mix | Theoretical | Proposition 3 / Corollary 1 proofs; unit test | Directly supported | Keep |
| 4 | 53 of 103 datasets contain duplicates; 37 ≥ 1%; 11 ≥ 30% | Empirical | rq1.* | Directly supported | Keep |
| 5 | Pre-specified H1 not supported (no family significant after Holm) | Empirical | main_alpha_0.1.p_H1_holm (min 0.092) | Directly supported | Keep, stated prominently |
| 6 | Gaps concentrated at high exposure; worst −6.9 pp (classification), −16.9 pp (regression) | Empirical | main_alpha_0.1.scp_gap_min; X2 strata | Directly supported (strata exploratory) | Keep; strata labelled exploratory |
| 7 | Gap correlates with exposure (10 of 16 families significant) | Empirical | spearman_exposure_gap, p_spearman (uncorrected, stated) | Directly supported | Keep |
| 8 | Seen-coverage term explains which datasets fail (ρ = 0.55) | Empirical, exploratory | exploratory.spearman_seen_excess_term_vs_gap | Partially supported (decomposition is partly an identity; the claim is about the size of the components) | Keep, described as a decomposition |
| 9 | cps88wages (conflicting labels) unaffected | Empirical, single case | X1 pairs | Directly supported for that dataset only | Narrowed to one dataset |
| 10 | External data: shortfalls up to −27.5 pp; 11/25 CIs below zero; MCP none below zero | Empirical | external.seedlevel | Directly supported | Keep |
| 11 | Injection: monotone dose–response for flexible learners; RF −12.4 pp at ρ = 1 vs limit −14.8 | Empirical, causal (controlled) | D_injection.* | Directly supported (all 37 planned datasets) | Keep |
| 12 | Capacity half of H5 not supported | Empirical | F_capacity.* | Directly supported (negative) | Keep |
| 13 | MCP restores nominal coverage; non-inferiority in all 16 families; size cost ≤ 4.4% | Empirical | main_alpha_0.1.mcp_gap_ci_lo, size_ratio_novel_median | Directly supported | Keep |
| 14 | solar_flare MCP shortfall is sampling noise (0.909 with 200 splits) | Empirical, verification | results/verification/solar_flare_200splits.json | Directly supported | Keep |
| 15 | Group-aware split near nominal | Empirical | H6_group_split | Directly supported | Keep |
| 16 | Calibration: novel overconfidence significant in 3/5 learners but small | Empirical | H4_calibration | Directly supported | Keep, small effect stated |
| 17 | Coverage decreases with distance to the nearest training record | Empirical, exploratory | E_distance_bins | Partially supported (medians only) | Keep as exploratory |
| 18 | Cost negligible | Empirical | tables/T9_cost.csv | Directly supported | Keep |
| 19 | Duplicate leakage inflates accuracy and changes rankings | Literature | Li (2026), Roth (2026) (preprints) | Literature-derived (non-peer-reviewed) | Keep, marked as preprints |
| 20 | "To our knowledge, effect on UQ not examined" | Literature / novelty | candidate_directions.md searches | Supported by documented searches (not exhaustive) | Keep, hedged |
| 21 | Practical threshold π̄ ≥ 0.1 | Interpretive | X2 strata | Interpretive, post hoc | Labelled as derived from our data |
| 22 | Typicality confound addressed by injection | Interpretive | Injection design | Interpretive | Keep |
| 23 | In regression, a distance-normalized score removes most of the shortfall (worst −3.4/−2.6 pp vs −15.8/−16.9 pp) | Empirical (baseline added in review round 2, pre-specified) | statistics.json → normalized_baseline; tables/T11 | Directly supported (regression, 12 datasets, RF/LightGBM only) | Keep; it tempers the remedy claim |
