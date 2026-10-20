# Selected target journal: Journal of King Saud University – Computer and Information Sciences (JKSU-CIS)

Decision date: 2026-10-20 (Research Director, after Agent 1's screen). Status: **Gate A passed, with
the caveats stated below.**

| Item | Value | Source / verification status |
|---|---|---|
| Journal | Journal of King Saud University – Computer and Information Sciences | Springer journal homepage (link.springer.com/journal/44443), fetched 2026-10-20 |
| Owner / publisher | King Saud University; published by Springer Nature (moved from Elsevier in 2025; DOIs 10.1007/s44443-…) | Springer homepage; Crossref DOI prefixes |
| ISSN (print, regulatory) / eISSN | 1319-1578 / 2213-1248 | Springer homepage |
| Publication model | Fully open access (APC payable on acceptance) | Springer homepage; DOAJ entry |
| APC | ≈ USD 1,990 / EUR 1,690 / GBP 1,490 (LetPub); DOAJ lists "up to USD 2,090". **Not verified on an official Springer fee page** | Secondary sources; must be confirmed by the author before submission |
| Journal Impact Factor | **6.4 (JCR 2025 release)**; 5-year JIF 6.0 | Springer homepage (Springer reproduces the Clarivate figure) |
| JCR category / quartile | COMPUTER SCIENCE, INFORMATION SYSTEMS — **Q1** (reported rank 6/149 for the JCR 2024 edition by OOIR, which mirrors Web of Science; Peeref and ivySCI also list JCR Q1 in this category) | **Secondary sources only.** Clarivate JCR is paywalled and could not be accessed. With JIF 6.4, Q1 in this category is highly plausible, but the quartile is reported as *Q1 per secondary sources, not verified directly in JCR*. Not mixed with the SCImago quartile (SJR 2025 = 1.434, Scopus Q1), which is a different system. |
| Editor-in-Chief | Nasser-Eddine Rikli | Springer homepage |
| Scope | "a refereed, international journal that covers all aspects of both foundations of computer and its practical applications" | Springer homepage overview |
| Peer review | Double-anonymous; usually two referees plus one Associate Editor; Editors-in-Chief make final decisions | Submission guidelines (fetched 2026-10-20) |
| Timeline evidence | Observed median submission→acceptance **72 days** (n = 1,054 articles published Oct 2025–Oct 2026; bootstrap 95% CI 70–74; IQR 55–98; 50.6% ≤ 72 days). For papers accepted since 1 Apr 2026: median **67 days**, 58% ≤ 72 days | Our Crossref analysis (`journal_comparison.md`, `data/jksu_full/`). Evidence level 3 (observed sample) |
| Official publisher timeline statistic | Not shown on the Springer homepage (no "submission to acceptance" figure displayed) | Springer homepage |

## Is the 72-day hard constraint satisfied?

**Borderline, and the most defensible verified match available.** Of ~40 assessed reputable non-MDPI
journals, JKSU-CIS is the only one with a credible, transparent, large-sample basis for a
submission-to-acceptance time of about 72 days. Its median equals the limit, and the recent cohort
(median 67 days) sits below it. The evidence does **not** support a guarantee: about 42–49% of
accepted papers took longer than 72 days, and desk-rejected or rejected papers are not in the
sample. No journal could offer a credible *maximum* of 72 days, because no publisher reports maxima
and every observed distribution has a long right tail.

Rather than silently relax the constraint, it is stated as follows: the selected journal is the only
assessed Q1 journal whose **typical (median) observed** submission-to-acceptance time meets 72 days.
A single submission has roughly a 50–58% observed chance of acceptance within 72 days, *conditional
on being accepted*.

## Why this journal fits the project

* The scope is broad computer science, explicitly including foundations and practical
  applications. Our contribution (validity of uncertainty quantification under record duplication,
  with theory, a remedy and a large benchmark study) is a methodological ML / data-quality
  contribution with direct practical consequences.
* The journal has recently published closely related work, e.g. "Conformal deep forest for
  uncertainty-aware classification" (2025, doi:10.1007/s44443-025-00175-3), "HF-DIF: hierarchical
  feature-selected deep isolation forest for unsupervised anomaly detection on tabular data" (2026,
  doi:10.1007/s44443-026-00706-6), "Representing uncertainty and imprecision in machine learning: a
  survey on belief functions" (2024, doi:10.1016/j.jksuci.2023.101904), and "Robust representation of
  domain incomplete tabular data via cross-modal debiasing and prototype-fused reconstruction" (2025,
  doi:10.1007/s44443-025-00225-w). Titles and DOIs were verified via the Crossref API on 2026-10-20.
* Word is preferred, and LaTeX is accepted for mathematical papers. The double-anonymous review and
  the "Statements and Declarations" requirements are documented in `journal_verification.md`.

## Principal editorial rejection risks

1. Readers of JKSU-CIS mainly see applied deep-learning papers. A statistical-methodology paper must
   make its practical stakes explicit early.
2. The contribution could be judged incremental if it is framed as "just Mondrian conformal
   prediction". The paper must lead with the *finding* (a silent guarantee failure on novel records,
   with a closed-form magnitude), and present the remedy as a necessary, validated complement.
3. Desk rejection for missing declarations or non-anonymized files.

## Backup strategy

No other assessed journal meets the timeline constraint, so there is no compliant backup. If
JKSU-CIS rejects the paper, the author must decide whether to relax the timeline. Non-compliant
candidates with strong scope fit are listed in `journal_comparison.md`: Machine Learning (Springer),
Data Mining and Knowledge Discovery, Statistics and Computing, Int. J. Data Science and Analytics.
