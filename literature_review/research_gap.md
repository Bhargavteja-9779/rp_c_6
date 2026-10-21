# Research-gap chain (Agent 3, verified by Agent 4)

**Evidence basis.** Bibliographic details of every cited work were verified against Crossref (DOIs),
the arXiv API or DataCite/Zenodo (`data/verified_dois*.json`). Full texts could **not** be read
inside this environment. Statements about content rest on abstracts, plus well-established
results for canonical conformal-prediction papers. The `evidence_basis` column of
`literature_matrix.csv` records this for each entry. Three guessed DOIs failed verification
(they resolved to unrelated papers) and were dropped; none is cited.

| Link | Content | Evidence |
|---|---|---|
| Existing knowledge | Split CP gives finite-sample **marginal** coverage under exchangeability (Papadopoulos et al. 2002; Lei et al. 2018; Vovk et al. 2022). Conditional coverage is impossible in general, but finite-group (Mondrian) coverage is achievable (Vovk 2012; Foygel Barber et al. 2021; Romano et al. 2020b; Gibbs et al. 2025) | Canonical results |
| Existing knowledge | Duplicate rows are common in standard tabular benchmarks: 75 of 156 audited datasets have ≥ 1 duplicate, and 20 have ≥ 30% duplicated rows. Random-split evaluation inflates accuracy and can change model rankings (Li 2026, preprint). Memorization leakage scales with capacity (Roth 2026, preprint). Domain audits show the same: NASA MDP (Gray et al. 2011; Shepperd et al. 2013) and KDD'99 (Tavallaee et al. 2009) | Preprint abstracts; peer-reviewed domain audits |
| Demonstrated limitation | All duplicate studies found measure **point performance** (accuracy, AUC, rankings). No study found quantifies the effect on **uncertainty quantification**, i.e. coverage of conformal sets or calibration, for records with versus without training copies. The CP literature evaluates on random row splits and reports marginal coverage (e.g. Romano et al. 2019; Angelopoulos & Bates 2023) | Searches recorded in `candidate_directions.md`: arXiv API, Crossref, extended web search; 0 relevant hits |
| Scientific consequence | A reported "90% guaranteed coverage" is an average over seen and novel rows. If seen rows are over-covered, novel rows, the deployment-relevant case for new entities, are under-covered by a predictable amount. Unlike optimistic accuracy, this undermines a **formal guarantee** practitioners rely on for risk-sensitive decisions | Proposition 1 (`research_design/theory.md`) |
| Proposed contribution | (i) Exact characterization and memorization limit (Prop. 1); (ii) label-free exposure prediction (Prop. 2); (iii) large-scale quantification across 103 datasets, 5 learners and 4 scores; (iv) a remedy with a guarantee for any deployment mix (Prop. 3, Cor. 1) and comparison with group-aware splitting; (v) the calibration analogue (overconfidence on novel rows) | — |
| Falsifiable hypotheses | H1–H6 in `research_design/research_questions.md` | — |
| Validating experiments | A–G in `research_design/experimental_protocol.md` | — |

## Artificial-gap check

* The gap is not "nobody applied CP to dataset X": it is a **mechanism** (Prop. 1) affecting every
  CP evaluation on data with repeated records.
* The remedy itself (Mondrian CP with a binary taxonomy) is **not** claimed as methodologically
  new. Mondrian CP is classical. What is new is the taxonomy's justification, its exactness
  argument under the finite-population split (Lemma 0), the deployment-mix corollary, and the
  empirical evidence that it is needed. The manuscript must say this explicitly.
* Applicability-domain work in cheminformatics (Norinder et al. 2014; Morger et al. 2021)
  recognises that CP behaves differently on "new" chemistry, but it concerns structural or
  temporal novelty, not exact record duplication or the seen/novel decomposition. It is cited as
  related work.
