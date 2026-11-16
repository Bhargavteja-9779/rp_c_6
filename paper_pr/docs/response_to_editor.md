---
title: "Response to the Editorial Office: PR-D-26-16249"
---

**Manuscript:** PR-D-26-16249 (Full Length Article, section: Machine learning)

**New title:** Duplicate Rows Inflate Conformal Coverage: A Simple Check and Fix for New Cases

Dear Editor,

Thank you for returning our manuscript with clear formatting instructions. We have rebuilt it in the required elsarticle template and addressed every point. The scientific content and all reported numbers are unchanged. To meet the page limit, some secondary tables and figures were moved to the Supplementary Material, and the text was tightened. Our responses follow, numbered as in your message.

**1. Title (10–15 words).** The title has been shortened to 13 words: *Duplicate Rows Inflate Conformal Coverage: A Simple Check and Fix for New Cases*. We will update the title in Editorial Manager to match.

**2. Single column, line spacing.** The manuscript is single-column. It uses the `review` option of elsarticle, which sets 1.5 line spacing, as specified in point 4.

**3. Template and length.** The source starts with `\documentclass[times, review, 10pt]{elsarticle}`. The manuscript is 35 pages including references, within the 35-page limit for a regular paper. Proofs, per-dataset tables and the deviation log are in a separate Supplementary Material file.

**4. Page layout.** The layout is:

- Letter paper with margins of 4.3 cm (top), 4.8 cm (right), 4.3 cm (bottom) and 4.8 cm (left).
- Times, with 10 pt body text and a title of about 14 pt.
- 8 pt for authors, captions and footnotes.
- 1.5 line spacing.
- Pages numbered at the foot, with the page number 2.6 cm from the bottom edge.

**5. Tables and figures within the margins.** All figures were redrawn at the text width of 118 mm, and none is rotated. The LaTeX log reports no overfull boxes, so no table, figure or line extends into the margins.

**6. Authors, float placement, page numbers.** Both authors are listed with their full affiliation: School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology, Vellore, India. P. N. Bhargav Teja is the first author and Rajay Vedaraj I. S. the corresponding author. Each table and figure appears near its first mention, and floats are kept within their own section. Every page is numbered.

**7. Abstract.** The abstract is one paragraph of 233 words.

**8. Conclusions.** The Conclusions section (Section 7) has been rewritten. It has separate paragraphs on strengths, weaknesses, benefits to the field and future work. It is about 520 words long, more than twice the abstract, and does not repeat it.

**9. Highlighting.** No text is highlighted or coloured, and all links are typeset in black.

**10. References.** The references now follow these rules:

- **Style.** References use the Elsevier numeric style (`elsarticle-num-names`). They appear in square brackets and are numbered in order of first citation.
- **Count and recency.** There are 54 references, within the required 35–55. Of these, 29 are from 2021 or later, 13 from 2024 or later, and 10 from 2026.
- **Recent work in this journal.** The list includes seven articles from *Pattern Recognition*, among them recent work on rank-based conformal prediction sets, score functions for rule-based classifiers, conformal e-prediction and adaptive conformal inference. Each is discussed in the literature review.
- **Diversity of sources.** Only three references are preprints, and they are cited because they are the most recent work on duplicated rows in tabular benchmarks. Published conference papers are cited in their published versions. The most frequent venues are *Pattern Recognition* and NeurIPS, with seven references each (13% of the list), so no single venue dominates.
- **No group citations.** In the running text, every reference now has its own comment; a citation such as "[3–7]" no longer appears. Only the comparison table (Table 1) cites two works per row. Each of those works is discussed individually in Section 2.

**11. Relevance to Pattern Recognition.** The paper concerns the reliability of uncertainty estimates from classifiers and regressors on tabular data. This is a pattern recognition problem with direct consequences for software defect prediction, network intrusion detection and phishing detection. It builds on recent conformal prediction work published in this journal, which is cited and discussed in Section 2. It contributes a model-free check, a calibration fix and a reporting rule, implemented as a Python tool.

**12. CRediT.** A CRediT authorship contribution statement is included after the Conclusions, with the roles of both authors. It is followed by the declaration of competing interest, the funding statement, the data-availability statement and the declaration on the use of generative AI. The data-availability statement gives the source of every data set, and the Supplementary Material lists a link to each of them. The code is available from the corresponding author on request.

**Corresponding author.** The manuscript names a single corresponding author, Rajay Vedaraj I. S. (rajay@vit.ac.in), as recorded in Editorial Manager.

We also provide the LaTeX source as a single self-contained file with its figures, which compiles with pdflatex. Highlights are supplied as a separate file.

Yours sincerely,

Rajay Vedaraj I. S. (corresponding author), on behalf of both authors
