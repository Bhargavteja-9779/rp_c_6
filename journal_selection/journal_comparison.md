# Journal comparison: observed submission-to-acceptance times (Gate A evidence)

**Verified on:** 2026-10-20. **Method:** `scripts/crossref_timeline.py`. For each candidate journal, Crossref
`assertion` metadata was retrieved for journal articles published 2026-01-01 → 2026-10-20 (max. 400
articles per journal in the screening pass). The *received* and *accepted* dates were read from that
metadata and the interval in days computed. Raw per-article data: `data/raw_<ISSN>.json`;
summaries: `data/timeline_summary_batch1.json`, `data/timeline_summary_batch2.json`,
`data/jksu_full/timeline_summary.json`.

**Evidence level:** level 3 of the project hierarchy (an independently verified sample of recent
articles with both dates). It is **not** an official publisher statistic and **not** a guarantee:

* Rejected papers never appear. The distribution describes accepted papers only (survivorship).
* "Received" is the original submission date deposited by the publisher. Article-type mix and
  special issues can shift the distribution.
* A median ≤ 72 days still means roughly half of accepted papers took longer than 72 days.
* Elsevier does not deposit received/accepted dates in Crossref, so Elsevier journals could only be
  checked against publisher-reported "submission to acceptance" figures quoted in web-search
  snippets of ScienceDirect pages. ScienceDirect blocks direct fetching from this environment, so
  those figures are lower-confidence. IEEE, Wiley/Hindawi, PeerJ and OUP titles deposited no dates
  for this window and could not be assessed by this method.

## Screening table (sorted by median days; window 2026-01-01 → 2026-10-20)

| Journal | Publisher | ISSN | n (with both dates) | Median days | IQR | P90 | Share ≤ 72 d |
|---|---|---|---|---|---|---|---|
| **Journal of King Saud University – Computer and Information Sciences** (full sample, pub. 2025-10 → 2026-10) | Springer Nature | 1319-1578 / 2213-1248 | **1054** | **72** (bootstrap 95% CI 70–74) | 55–98 | 128 | **0.51** |
| ↳ same journal, papers *accepted* since 2026-04-01 | | | 581 | **67** | | | **0.58** |
| Journal of Intelligent Information Systems | Springer Nature | 0925-9902 | 75 | 131 | 96–162 | 275 | 0.07 |
| Systems Science & Control Engineering | Taylor & Francis | 2164-2583 | 78 | 131.5 | 105–173 | 227 | 0.08 |
| Scientific Reports | Springer Nature | 2045-2322 | 397 | 132 | 93–204 | 274 | 0.12 |
| Journal of Cheminformatics | Springer Nature | 1758-2946 | 172 | 132 | 105–179 | 248 | 0.07 |
| Cybersecurity | Springer Nature | 2523-3246 | 244 | 132 | 96–180 | 245 | 0.12 |
| J. King Saud Univ. – Engineering Sciences | Springer Nature | 1018-3639 | 57 | 136 | 98–207 | 264 | 0.10 |
| Machine Intelligence Research | Springer Nature | 2731-538X | 70 | 136.5 | 94–174 | 224 | 0.11 |
| BMC Bioinformatics | Springer Nature | 1471-2105 | 338 | 138 | 99–214 | 302 | 0.12 |
| Int. J. Computational Intelligence Systems | Springer Nature | 1875-6883 | 393 | 140 | 92–211 | 301 | 0.14 |
| International Journal of Digital Earth | Taylor & Francis | 1753-8947 | 237 | 144 | 114–177 | 216 | 0.01 |
| Complex & Intelligent Systems | Springer Nature | 2198-6053 | 317 | 156 | 105–239 | 377 | 0.06 |
| BMC Medical Informatics and Decision Making | Springer Nature | 1472-6947 | 396 | 160.5 | 105–315 | 604 | 0.11 |
| Journal of Cloud Computing | Springer Nature | 2192-113X | 172 | 160.5 | 70–265 | 367 | 0.26 |
| Journal of Intelligent Manufacturing | Springer Nature | 0956-5515 | 233 | 161 | 118–213 | 279 | 0.07 |
| Int. J. Data Science and Analytics | Springer Nature | 2364-415X | 338 | 168 | 112–261 | 381 | 0.09 |
| Arabian Journal for Science and Engineering | Springer Nature | 2193-567X | 394 | 168 | 117–247 | 328 | 0.07 |
| EPJ Data Science | Springer Nature | 2193-1127 | 97 | 182 | 145–252 | 284 | 0.02 |
| Artificial Intelligence Review | Springer Nature | 1573-7462 | 260 | 188.5 | 139–250 | 343 | 0.04 |
| Machine Learning | Springer Nature | 0885-6125 | 231 | 206 | 165–312 | 448 | 0.03 |
| Applied Intelligence | Springer Nature | 0924-669X | 388 | 234 | 173–345 | 481 | 0.01 |
| Data Mining and Knowledge Discovery | Springer Nature | 1384-5810 | 103 | 243 | 156–370 | 589 | 0.02 |
| Statistics and Computing | Springer Nature | 0960-3174 | 191 | 250 | 179–324 | 436 | 0.01 |
| Journal of Big Data | Springer Nature | 2196-1115 | 215 | 257 | 187–367 | 460 | 0.01 |
| Neural Computing and Applications | Springer Nature | 0941-0643 | 400 | 269.5 | 187–378 | 579 | 0.01 |
| Knowledge and Information Systems | Springer Nature | 0219-1377 | 259 | 289 | 189–413 | 592 | 0.02 |
| Int. J. Machine Learning and Cybernetics | Springer Nature | 1868-8071 | 399 | 293 | 259–316 | 369 | 0.01 |
| Cognitive Computation | Springer Nature | 1866-9956 | 112 | 303 | 169–454 | 682 | 0.07 |
| Journal of Computational and Graphical Statistics | Taylor & Francis | 1061-8600 | 167 | 348 | 271–455 | 605 | 0.02 |
| Journal of Applied Statistics | Taylor & Francis | 0266-4763 | 127 | 365 | 262–521 | 771 | 0.00 |
| Soft Computing | Springer Nature | 1432-7643 | 166 | 366 | 242–570 | 1214 | 0.01 |

Journals with too few dated records (n < 20) for a meaningful estimate: J. Experimental & Theoretical AI
(n = 16, median 327.5), Applied Artificial Intelligence (n = 10, median 156), Neural Processing Letters
(n = 1). Journal of Supercomputing, PeerJ Computer Science and Journal of Computational Design and
Engineering (OUP) deposited no dates.

## Elsevier titles (publisher-reported figures seen only in search snippets; lower confidence)

| Journal | Reported "submission to acceptance" | Status vs 72-day constraint |
|---|---|---|
| Results in Engineering | 74 days (ScienceDirect Insights snippet) | **Fails** (74 > 72); closest Elsevier near-miss |
| Alexandria Engineering Journal | 106–130 days (snippets disagree) | Fails |
| Egyptian Informatics Journal | 183 days | Fails |
| Computers & Electrical Engineering | 169 days | Fails |
| Computer Science Review | 201 days | Fails (and review-only) |

Expert Systems with Applications, Knowledge-Based Systems, Information Sciences and Pattern Recognition
publish no Crossref dates. No snippet evidence was found that any of them is close to 72 days, so they
are classified **TIMELINE UNVERIFIED — DOES NOT SATISFY THE HARD CONSTRAINT**.

## Excluded by rule

* MDPI titles: excluded by project rule.
* IEEE Access, Scientific Reports: not defaulted to. Scientific Reports was assessed anyway (median
  132 days) and fails the timeline.

## Result

Only one reputable, non-MDPI journal in the screen reaches a median submission-to-acceptance time of
≤ 72 days with a large, transparent sample: **Journal of King Saud University – Computer and
Information Sciences**. The next fastest (Results in Engineering, 74 days self-reported) narrowly
fails. Every other assessed computer-science / AI journal needs at least 130 days at the median.
