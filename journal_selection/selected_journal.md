# Selected target journal (revised 2026-10-21): Pattern Recognition (Elsevier)

## Why the target changed

The user dropped the 72-day submission-to-acceptance constraint. The new instruction is: target a
**high-impact-factor journal** and maximize the chance of **acceptance**. No journal can guarantee
acceptance. The selection below maximizes impact factor *subject to* a demonstrated editorial
appetite for this kind of contribution: conformal-prediction methodology and evaluation with
elementary but exact theory, a large empirical study and a practical remedy.

The previous target, JKSU-CIS (JIF 6.4; median 72 days to acceptance), is kept as the fast,
broad-scope fallback. Its package (`manuscript/Final_Manuscript.docx`) remains valid.

## Evidence used

1. **Receptiveness:** the number of papers with "conformal" in the title published 2023–2026,
   counted per candidate journal through the Crossref API (`data/conformal_paper_counts.json`;
   query "conformal prediction", top-600 relevance hits per journal, titles checked).
2. **Impact factor:** secondary sources only, because Clarivate JCR is paywalled and ScienceDirect
   journal pages are blocked from this environment. Figures disagree between sources and are
   reported as ranges.

| Journal | Publisher | 2025 JIF (secondary sources) | Conformal-titled papers 2023–26 | Fit for this paper | Main risk |
|---|---|---|---|---|---|
| **Pattern Recognition** | Elsevier | 7.6–9.1 (sources disagree), JCR Q1 | **19** (part from a 2024–25 special issue on conformal prediction, now closed; regular-issue papers also in 2026, incl. two Mondrian papers) | **High**: active conformal community; recent Mondrian work in the journal | Selective; novelty bar for methods |
| Knowledge-Based Systems | Elsevier | 7.6–9.6, Q1 | 3 (applied) | Medium | Expects applied systems |
| Expert Systems with Applications | Elsevier | 7.5–9.4, Q1 | 3 (applied CP intervals) | Medium–low | Application focus; very long review times reported |
| Information Sciences | Elsevier | 6.8–7.7, Q1 | 1 | Low–medium | Few CP papers |
| IEEE TNNLS | IEEE | ≈ 10 | 3 | Low | Novelty bar for neural-network methods; elementary theory |
| Neurocomputing | Elsevier | ≈ 5.5–6.5 | 6 (incl. a conformal software paper) | Medium–high | Lower IF |
| Machine Learning | Springer | ≈ 2.9–4 | 6 | High | Low IF |
| JKSU-CIS (previous) | Springer Nature | 6.4 | 1 | Medium | Broad audience |

## Decision

**Primary target: Pattern Recognition (ISSN 0031-3203, Elsevier).** It has the highest impact factor
among journals with a demonstrated, recent appetite for conformal-prediction methodology,
including Mondrian calibration:

* Seo et al. (2026), Calibrated Mondrian CP for spatial modeling, 180:114113.
* Zhang & Zhou (2026), Mondrian conformal predictive system, 172:112338.

**Cascade if rejected:** Neurocomputing → JKSU-CIS (package ready) → Machine Learning
(best topical fit, lower IF).

## Requirements applied (official guide confirmed through search snippets; full page not fetchable)

* 20–35 pages including figures, tables, references and biographies (appendices excluded). Our
  review-format build (12 pt, double spacing) is 31 pages.
* Abstract ≤ 250 words (ours: 234); 3–5 highlights of ≤ 85 characters (ours: 5, max 79); 1–7
  keywords (ours: 6).
* Author biographies required (placeholder).
* Declaration of generative-AI use at submission (included).
* Elsevier declarations: CRediT, competing interests, funding, data availability.
* References: numbered in order of citation.
* Review model: reported as single-anonymized (Wikipedia; not verified on the official page).
  The manuscript is anonymized anyway and a separate title page is supplied, which is compatible
  with either model.

## Honest acceptance assessment

* Strengths for this journal: exact theory, a large pre-specified study, causal and external
  evidence, an open pipeline, and a practical recommendation.
* Main risk: reviewers may judge the remedy (standard Mondrian CP) and the elementary theory
  incremental, and the primary hypothesis was not supported on typical benchmarks.
* Mitigations: the paper is framed around the exact characterization, the predictability of
  failure and the external evidence; it states clearly what is not new.
* No acceptance probability can be stated credibly. Desk rejection at a selective Q1 journal is a
  real possibility, so the cascade above is part of the plan.
