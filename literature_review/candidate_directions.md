# Phase 1: candidate research directions (Agents 2, 4, 5)

Screening criteria: importance, novelty potential after a prior-art check, feasibility on the
available hardware (4 CPU cores, 15 GB RAM, no GPU), public data, theoretical potential, and fit
with JKSU-CIS. "Prior-art check" means the searches actually run (arXiv API, Crossref, web search)
and recorded in this file. It is not an exhaustive systematic review.

Scores are 1–5 (5 = best). **Kill** = rejected at the novelty or feasibility gate.

| # | Direction | Key prior art found | Novelty | Feasibility | Significance | Decision |
|---|---|---|---|---|---|---|
| 1 | Audit of exact/near-duplicate rows in tabular benchmarks and the resulting accuracy inflation | Li (2026, Zenodo preprint "Rows are not samples", 161 datasets); arXiv:2604.04199 (2,047 datasets, memorization leakage); Early-stage-diabetes case study (Research Square 2026) | 1 | 5 | 4 | **Kill**: already done in 2026 |
| 2 | Phishing-URL detectors: dataset artifacts and cross-dataset collapse | Several 2025–2026 cross-dataset studies (Wiley S&P 2026, XGBoost cross-dataset, XAI feature-trust) | 2 | 4 | 3 | **Kill**: crowded |
| 3 | Optimal train/calibration split ratio in split conformal prediction | arXiv:2606.31600 "On optimal data splitting for split conformal prediction" (2026) | 1 | 5 | 3 | **Kill** |
| 4 | Class-conditional CP for many or rare classes via shrinkage | Ding et al. (NeurIPS 2023, clustered CP); RC3P (2024); Kandinsky CP (2025) | 2 | 4 | 3 | Kill: crowded, incremental |
| 5 | Conformal prediction with missing covariates | Zaffran et al. (ICML 2023; 2024) | 1 | 4 | 3 | Kill |
| 6 | Adaptive conformal inference step size for time series | Gibbs & Candès (2021, 2024); Zaffran et al. (2022); Angelopoulos et al. (2023, conformal PID) | 1 | 4 | 3 | Kill |
| 7 | Label-noise-robust conformal classification | Einbinder et al. (2022/24); Sesia et al. (2024); Penso & Goldberger (2024) | 2 | 4 | 3 | Kill |
| 8 | TabPFN / tabular foundation-model calibration | Multiple 2025–2026 papers incl. arXiv:2609.34887 (C-USIM) | 2 | 2 (CPU-bound weights) | 4 | Kill |
| 9 | Fairness-metric uncertainty in small subgroups | Lum et al. (FAccT 2022); Ji et al. (NeurIPS 2020) | 2 | 5 | 3 | Kill |
| 10 | Predictive multiplicity / seed arbitrariness in GBDT | Marx et al. (ICML 2020); Black et al. (FAccT 2022); Cooper et al. (2024) | 2 | 5 | 3 | Kill |
| 11 | Leakage in synthetic-tabular-data utility evaluation (generator sees test data) | Synthcity; Ganev & De Cristofaro (2023); partially discussed in privacy literature | 3 | 3 | 3 | Hold (third) |
| 12 | Hierarchical / repeated-measures data in CP | Dunn, Wasserman & Ramdas (JASA 2023); Lee, Barber & Willett (NeurIPS 2023) | 1 | 4 | 4 | Kill |
| 13 | Scientometric study of peer-review delays from Crossref assertions | Björk & Solomon (2013); Huisman & Smits (2017); Hanson et al. (QSS 2024) | 2 | 5 | 3 | Kill: crowded, and off-scope for JKSU-CIS |
| 14 | Approximate nearest-neighbour search early termination | Li et al. (SIGMOD 2020) and many follow-ups | 2 | 4 | 3 | Kill |
| 15 | Calibration-set double-dipping (early stopping or tuning on the CP calibration set) | Yang & Kuchibhotla (2021/2024); Liang et al. (2024); arXiv:2502.03023 (tuning-bias scaling law) | 1 | 5 | 3 | Kill |
| 16 | **Effect of duplicate records on the validity of conformal prediction (and calibration) for novel records; novelty-conditional remedy with guarantee** | No prior work found. Searches: arXiv API `abs:conformal AND abs:duplicates` (0 relevant hits); Crossref "conformal prediction duplicate records", "conformal prediction data leakage" (0 relevant); extended web search (0 relevant). Closest: duplicate audits for *accuracy* (#1); applicability-domain CP in cheminformatics (Norinder et al. 2014); difficulty-Mondrian CP (Boström & Johansson 2020); conditional-coverage theory (Vovk 2012; Gibbs et al. 2025) | 4 | 5 | 4 | **Selected** |
| 17 | Near-duplicate / distance-to-training coverage decay in CP | Localized CP (Guan 2023); kNN-difficulty normalization (Papadopoulos et al. 2011; Boström & Johansson 2020) | 2 | 5 | 3 | Folded into #16 as an exploratory extension |

## Why #16 survives

1. **Real limitation with consequences.** The marginal guarantee of split CP is stated over *rows*.
   When rows duplicate the same record (KDD-style logs, NASA defect metrics, survey profiles), a
   practitioner who deploys on *new* records receives a weaker guarantee than the one they report.
   Li (2026) shows duplication is common: 52 of 156 audited datasets have ≥ 1% duplicated rows and 20
   have ≥ 30%. The UQ consequence has not been quantified.
2. **Mechanism plus closed form.** Under memorization, novel-record miscoverage inflates from α to
   about α/(1 − π), where π is the fraction of test rows that have a training copy (Proposition 1 in
   `research_design/theory.md`). This is testable and falsifiable.
3. **Remedy with a finite-sample guarantee** (novelty-Mondrian CP), plus a validated alternative
   (group-aware splitting), both cheap.
4. **Feasible**: OpenML-CC18 and OpenML-CTR23 are public and CPU-friendly.
5. **Value even if effects are small.** If most datasets show negligible gaps, the paper still
   delivers the closed-form exposure bound, the audit tool, and the honest finding that only heavily
   duplicated datasets matter. That narrows its claims but keeps it useful.

A pilot on 5 datasets (`research_design/pilot/pilot.py`, exploratory and **not** confirmatory
evidence) found novel-record coverage of 0.83–0.84 at nominal 0.90 on kc1 (π ≈ 0.47), 0.89 on
spambase (π ≈ 0.10), and exactly nominal on a duplicate-free control (Bioresponse). The pilot was
used only to confirm feasibility before the protocol was frozen.
