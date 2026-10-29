# Claim–evidence matrix (revised manuscript, v2)

| # | Claim in the paper | Where | Evidence (file) | Status |
|---|---|---|---|---|
| 1 | Random splits can report about 90% coverage while new cases are covered far less (mc1: 91.7% vs 62.7%) | Abstract, §1, §5 | `results/reinforcement/tables/case_studies.csv` | Supported |
| 2 | Separate calibration restores new-case coverage in the applications | §5, Fig. 1 | same | Supported (89.4–94.5%) |
| 3 | The check can miss (kc2) and can raise false alarms (kc3) | §5 | same | Reported |
| 4 | Exposure formula (2) predicts seen share (MAE 0.0012) | §6.1 | `results/statistics.json`, `tables/T1_audit.csv` | Supported |
| 5 | No typical shortfall across 103 benchmarks (H1 not supported) | Abstract, §6.1, §8.3 | `results/statistics.json` | Supported (negative result) |
| 6 | Shortfall grows with copying, for flexible learners | §6.2, Fig. 2 | `results/inject/`, `statistics.json` (D_injection) | Supported |
| 7 | Capacity variation within a learner: effect not detected | §6.2 | `statistics.json` (F_capacity) | Reported as inconclusive |
| 8 | Eq. (3) ranks retrospective shortfalls (ρ = 0.72, RF) | §6.1 | `results/reinforcement/statistics_reinforcement.json` (retrospective) | Supported, non-blind |
| 9 | On fresh data the fix keeps new-case coverage on target (P3) | §7.1 | `statistics_reinforcement.json` (P3), `tables/prospective_per_dataset.csv` | Supported |
| 10 | On fresh data Eq. (3) holds as a limit (P2, 20/20) | §7.1 | `statistics_reinforcement.json` (P1_P2_P5) | Supported |
| 11 | On fresh data Eq. (3) does not rank data sets (P1) | Abstract, §7.1, §8.3 | same | Supported (negative result) |
| 12 | The safety margin reduces unlucky splits; not significant after Holm (P4) | §7.1 | `statistics_reinforcement.json` (P4, holm_primary) | Reported |
| 13 | Purity removes exposure-only false alarms; screen has no RF/LightGBM misses | §7.1, Fig. 4 | `tables/prospective_scp_purity.csv`; `numbers_v2.py` (pr_gs_*, pr_gp_*) | Supported (descriptive) |
| 14 | The rule in §8.1 was written before the fresh results | §7.1 | git: `aafc419` (13:42 UTC) vs first fresh result 14:24 UTC | Verified |
| 15 | Exact keys miss near-copies; distance-based calibration stays on target | §7.2, Fig. 5 | `tables/neardup_summary.csv`, `statistics_reinforcement.json` (neardup) | Supported |
| 16 | Fix costs little in set size and compute | §6.3 | `statistics.json`, `tables/T9_cost.csv` | Supported |
| 17 | Normalized score removes most regression shortfall, without guarantee | §6.3 | `tables/T11_normalized_baseline.csv` | Supported |
| 18 | Validity of separate calibration for any seen/new mix | §3.4, App. A | Proof (Vovk et al. 2022 argument), unit tests | Supported (theory) |
