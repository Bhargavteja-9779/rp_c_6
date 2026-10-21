"""Title page and cover letter (python-docx). Author-specific fields are explicit placeholders;
nothing about authors, affiliations, funding or originality is asserted on the authors' behalf."""
import json
import os
import sys

from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from numbers_from_results import compute_numbers  # noqa: E402

TITLE = ("Seen or new? Duplicate records, conformal coverage on novel inputs, and a novelty-conditional "
         "remedy for tabular benchmarks")


def _doc():
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    return d


def title_page():
    d = _doc()
    d.add_heading("Title page", level=1)
    d.add_paragraph().add_run(TITLE).bold = True
    for label in ["Author names (in final order)", "Affiliations (department, institution, city, country)",
                  "Corresponding author and active e-mail address", "ORCID iDs (16 digits, if available)",
                  "Acknowledgments", "Funding statement", "Competing interests statement",
                  "Author contributions (CRediT)"]:
        p = d.add_paragraph()
        p.add_run(f"{label}: ").bold = True
        p.add_run("[AUTHOR TO COMPLETE]")
    d.add_paragraph("This title page is supplied separately because JKSU-CIS uses double-anonymous review; "
                    "the manuscript file itself contains no identifying information.")
    d.save(os.path.join(HERE, "title_page.docx"))


def cover_letter(n):
    d = _doc()
    d.add_paragraph("[DATE]")
    d.add_paragraph("Editor-in-Chief\nJournal of King Saud University – Computer and Information Sciences")
    d.add_paragraph("Dear Editor,")
    body = [
        f"We submit the manuscript “{TITLE}” for consideration as a research article in the Journal of King Saud "
        "University – Computer and Information Sciences.",
        "Conformal prediction is increasingly used to attach guaranteed uncertainty to machine-learning predictions, "
        "and its guarantee is usually checked on random row splits of benchmark data. The manuscript asks what this "
        "guarantee means when a dataset contains duplicated records, so that some test rows have exact copies in the "
        "training data. We derive an exact expression for coverage on genuinely new records, a label-free formula that "
        "predicts exposure from duplicate-group sizes, and a novelty-conditional (Mondrian) remedy that is valid for "
        "any mix of seen and new records.",
        f"A pre-registered evaluation on {n['n_total']} OpenML-CC18 and OpenML-CTR23 datasets, with five learners and "
        "four nonconformity scores, shows that the exposure formula is almost exact (mean absolute error "
        f"{n['exp_mae']}). It also shows that the primary hypothesis of a typical shortfall was not supported: median "
        f"gaps were {n['h1x_gap_median_min']} to {n['h1x_gap_median_max']} percentage points. Shortfalls are "
        f"concentrated in a predictable minority of datasets, reaching {n['h1_worst_gap']} points, and controlled "
        "duplicate-injection experiments reproduce the predicted dose–response. We report this negative primary "
        "result openly, together with the mechanism that explains it. All code, raw results and the analysis "
        "pipeline will be released.",
        "We believe the work suits the journal's readership because it addresses the foundations of reliable "
        "machine-learning evaluation and has direct consequences for practitioners who deploy uncertainty-aware "
        "models on tabular data.",
        "[AUTHOR TO CONFIRM: This manuscript is original, has not been published, and is not under consideration "
        "elsewhere. All authors have approved the submission. We declare no competing interests.] "
        "[AUTHOR TO COMPLETE: re-used or unpublished material, if any; suggested reviewers, if desired.]",
        "The manuscript was prepared with substantial assistance from an AI system, as described in its "
        "“Use of AI tools” statement.",
        "Sincerely,\n[CORRESPONDING AUTHOR NAME, AFFILIATION, E-MAIL]",
    ]
    for b in body:
        d.add_paragraph(b)
    d.save(os.path.join(HERE, "cover_letter.docx"))


if __name__ == "__main__":
    nums = compute_numbers(os.path.join(os.path.dirname(HERE), "results"))
    title_page()
    cover_letter(nums)
    print("ok")
