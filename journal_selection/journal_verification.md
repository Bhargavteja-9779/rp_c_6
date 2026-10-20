# JKSU-CIS author-guideline checklist (Step 1)

Source: Springer submission guidelines page for journal 44443, fetched 2026-10-20 through the
Springer authentication redirect. Items marked † must be re-checked by the corresponding author in
the Editorial Manager interface at submission time. The page itself says the guidelines are being
revised.

| Requirement | Guideline | How the package complies |
|---|---|---|
| File format | Word (.docx) preferred; LaTeX accepted for mathematical content; editable source required at every submission | `manuscript/Final_Manuscript.docx` (editable source) plus PDF for review |
| Title | Concise and informative | ✔ |
| Abstract | 150–250 words, no undefined abbreviations or citations | Checked by word count in `manuscript/build_manuscript.py` |
| Keywords | 4–6 | 6 keywords |
| Headings | Decimal numbering, ≤ 3 levels | ✔ |
| Review model | **Double-anonymous**: no names, affiliations or identifying self-citations in the manuscript | Manuscript is anonymized. The title page is a separate file (`manuscript/title_page.docx`) |
| Title page | Names, affiliations, corresponding e-mail, ORCID, acknowledgments, funding, disclosures | Placeholders marked **[AUTHOR TO COMPLETE]**. No author details are fabricated |
| Citation style | Springer author–year, e.g. "(Thompson 1990)"; reference list alphabetical; DOIs where available; LTWA journal abbreviations | Author–year in text; alphabetical list with DOIs |
| Figures | EPS (vector) / TIFF (halftone); line art ≥ 1200 dpi, halftone ≥ 300 dpi; Helvetica/Arial 8–12 pt; widths 84 or 174 mm; files named Fig1…; captions in the manuscript text, starting with bold "Fig." | Figures exported as EPS + 600-dpi TIFF + PNG, sized to 84/174 mm, Arial |
| Tables | Use the word processor's table function; numbered; captions | ✔ (python-docx tables) |
| Statements and Declarations (after references) | Competing interests (**required**), Funding (**required**), Author contributions (encouraged), Ethics approval / consent (if humans or animals), Data availability (**required for original research**), code (encouraged under the SN data policy) | All included. Ethics: not applicable (public, de-identified benchmark data). Funding / competing interests: **[AUTHOR TO CONFIRM]** |
| Data policy | Springer Nature research data policy; deposit in repositories; cite datasets with persistent identifiers; anonymize repository during double-anonymous review | All datasets are public OpenML datasets cited by ID. Code is in a git repository that must be deposited (e.g. Zenodo) and anonymized for review† |
| LLM / AI use | LLMs cannot be authors; LLM use beyond copy-editing must be documented in Methods (or a suitable section) | The manuscript has an explicit "Use of AI tools" statement describing the AI-assisted workflow. The human authors remain accountable and must review and approve it |
| Cover letter | Transparency about re-used / unpublished material | `manuscript/cover_letter.docx` |
| Originality | Submission implies the work is unpublished, not under consideration elsewhere, and approved by all co-authors | Must be confirmed by the author; not asserted on the author's behalf |
| Authorship changes after acceptance | Not permitted | The author must fix the author list before submission† |
