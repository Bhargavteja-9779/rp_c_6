# Novelty map (Agent 4)

| Closest work | What it established | What remains open | What we add | How it is measured | What would falsify our novelty claim |
|---|---|---|---|---|---|
| Li (2026) "Rows are not samples" (preprint) | Duplicate prevalence in OpenML/UCI suites; exposure probability under K-fold; +1.5 pp mean accuracy optimism; ranking distortion | Effect on uncertainty quantification and calibration; a validity-preserving remedy with a guarantee | Coverage decomposition, memorization limit, CP/calibration evidence, Mondrian remedy | Experiments A–D | A version of Li (2026) or other work reporting CP coverage on seen vs novel records. Checked against the Zenodo abstract (2026-10-03): not covered |
| Roth (2026) leakage landscape (arXiv:2604.04199) | Memorization leakage (AUC inflation) scales with capacity | UQ validity | As above | — | Same check: AUC only |
| Romano et al. (2020b) "With malice toward none" | Marginal CP can under-cover protected groups; group-wise calibration fixes this | Groups defined by *train membership* (data-dependent but label-free); the duplicate mechanism; exactness under a finite-population split; closed-form gap | Lemma 0 + Prop. 1–3; empirical prevalence | Theory + Exp. B/C | A paper deriving α/(1−π) or seen/novel Mondrian CP |
| Vovk (2012); Vovk et al. (2022) Mondrian CP | Category-conditional validity for any taxonomy fixed before calibration | Which taxonomy matters for duplicated data, and why | Choice of taxonomy + justification + evidence | — | — (Mondrian itself is not claimed as new) |
| Gibbs, Cherian & Candès (2025) | Conditional coverage over function classes, incl. overlapping groups | The specific group and its practical stakes | Same | — | — |
| Boström & Johansson (2020); Papadopoulos et al. (2011) | Difficulty- or kNN-distance-based normalization and binning | Exact-duplicate seen/novel split; duplicates as the cause | Exploratory distance analysis (Exp. E) is presented as an **instance** of their approach, not as new | — | — |
| Elangovan et al. (2021); Lewis et al. (2021) | Overlap-stratified *accuracy* in NLP | Stratified *coverage*, tabular | Seen/novel stratified coverage | — | — |
| Norinder et al. (2014); Morger et al. (2021) | CP and applicability domain; CP miscalibration on temporally new data | Duplicate mechanism | — | — | — |

**Verdict (Agents 0, 3, 4, 5):** a defensible contribution exists. The claim is the
*finding plus its exact quantification plus validated remedy*, not a new algorithm. Wording to
avoid: "first to propose Mondrian CP", "novel conformal method". Wording supported by the
evidence (subject to the final searches): "to our knowledge, the first systematic quantification
of how duplicate records affect conformal coverage on novel records".
