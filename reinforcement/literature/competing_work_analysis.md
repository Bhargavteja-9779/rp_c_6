# Competing-work analysis (reinforcement cycle; same content as audit/novelty_reassessment.md, kept here for the literature folder)

New searches in this cycle (2026-10-21): arXiv API queries for conformal + {leakage,
memorization, "train-test overlap", "near-duplicate", "group split"} and Mondrian + conformal +
novelty, sorted by date; two extended web searches. They are recorded in this cycle's session log;
abstracts were read for every hit judged relevant.

## Competitive research matrix (closest work)

| Work | Status | Question | Method / data | Strongest result | Overlap with ours | Remaining opportunity |
|---|---|---|---|---|---|---|
| Li 2026, *Rows are not samples* (Zenodo) | Preprint | Do duplicate rows bias tabular benchmark accuracy and rankings? | Audit of 156 OpenML/UCI datasets; group-aware CV | +1.5 pp mean accuracy optimism, up to +40 pp; leader changes on a quarter of duplicated datasets | Prevalence; the exposure probability for K-fold (analogous to our Prop. 2) | No uncertainty quantification |
| Roth 2026, arXiv:2604.04199 | Preprint | Which leakage classes matter? | 2,047 datasets, injection | Memorization leakage scales with capacity (AUC) | Injection design | No UQ |
| **Deng 2026, arXiv:2609.29580 (new)** | Preprint | Repeated rows in anomaly-detection benchmarks | Exact-row audit of 690 OddBench datasets; support- vs row-weighted AUROC; SCOUT detector with factorwise **split-conformal FPR control**, invariant to replication | Train-test overlap in 355/690 datasets; AUROC changes ≥ 0.05 on 50–61 datasets | Exact-row audit; conformal calibration in the presence of replication | Unsupervised FPR control, not supervised prediction-set coverage for novel records. No seen/novel decomposition, no exposure-to-coverage law, no purity bound |
| **Tareaf et al. 2026, arXiv:2609.11838 (new)** | Preprint | Leakage in survey-based cardiovascular screening | 10 classifiers; feature-leakage tiers | Marginal CP under-covers subgroups (0.82–0.86); Mondrian repairs every stratum | Mondrian repair of under-covered strata | Strata are demographic, not novelty |
| Romano et al. 2020b (HDSR) | Peer-reviewed | Equalized coverage for protected groups | Group-conditional CP | Group under-coverage, Mondrian fix | Same mechanism class | Groups fixed a priori, not induced by the split |
| Vovk 2012; Vovk et al. 2022 | Peer-reviewed | Conditional validity; Mondrian CP; training-conditional (PAC) validity | Theory | Category-conditional and PAC guarantees | Our Prop. 3 and PAC thresholds are applications | — |
| Gibbs et al. 2025 (JRSSB) | Peer-reviewed | Conditional guarantees over function classes | LP-based calibration | Exact coverage over a finite-dimensional class | Reduces to Mondrian for disjoint groups | — |
| Papadopoulos et al. 2011; Boström & Johansson 2020 | Peer-reviewed | Adaptive / difficulty-Mondrian CP | kNN difficulty | Adaptive intervals | Our normalized and distance baselines | Not studied as a duplicate remedy |
| Dunn et al. 2023 (JASA) | Peer-reviewed | CP for new groups in hierarchical data | Known group IDs | Validity for a new group | Group-level novelty | Requires known IDs; no exposure law |

## Novelty stress test

| Question | Answer |
|---|---|
| Is the main contribution already known? | The *mechanism class* (marginal CP under-covers a subgroup) is known. Its instance for train-membership groups induced by duplication, with an exposure law, a purity law and a large-scale quantification, was not found in any source. Deng 2026 is the closest and addresses a different task (unsupervised FPR) |
| Does the method introduce a new principle? | No; the remedies are standard (Mondrian, PAC thresholds, normalized scores). The paper must not claim methodological novelty |
| Only a combination of established components? | The remedy, yes. The new *knowledge* is the predictive characterization (Props. 2 and 4) and its prospective validation |
| Mainly an application of a standard model to new data? | No; it is an evaluation-validity study with theory |
| Gap supported by primary evidence? | Yes, for UQ under duplication (searches: no supervised-CP duplicate study) |
| Are the differences material and demonstrable? | Yes: 5–28 pp coverage differences on at-risk data; demonstrable prospectively if U1 succeeds |
| Would removing the claimed novelty invalidate the paper? | If Prop. 4 fails prospectively, the paper keeps only the descriptive and exposure contributions, a weaker but still honest benchmark-note contribution |

## Path decision

**Path A + B: strengthen and reformulate.** The contribution is reformulated from "duplicates
break CP; here is a remedy" to "**when and by how much** duplicates break CP for new records can
be predicted *before training* from two label-level audit quantities (exposure and label
purity). The prediction is validated prospectively, and standard calibration remedies restore
validity." No new algorithm is invented (Path C rejected: no evidence it is needed). Path D is
held in reserve if U1 fails.
