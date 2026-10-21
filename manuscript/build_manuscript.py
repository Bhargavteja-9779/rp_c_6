"""Assemble the manuscript from section files, fill every number from results/, and render
DOCX (pandoc, native Word equations) and PDF (LibreOffice).

Placeholders have the form {{key}}; keys are produced by `numbers.py` from results/statistics.json
and results/tables/*.csv, so every reported number traces to a machine-readable result.
Unresolved placeholders abort the build.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from numbers_from_results import compute_numbers  # noqa: E402

SECTIONS = ["00_front.md", "01_intro.md", "02_related.md", "03_theory.md", "04_methods.md", "05_results.md",
            "06_discussion.md", "07_conclusion.md", "08_declarations.md", "90_references.md"]


def fill(text, nums):
    def rep(m):
        k = m.group(1).strip()
        if k not in nums:
            raise KeyError(f"unresolved placeholder {{{{{k}}}}}")
        return str(nums[k])
    return re.sub(r"\{\{([^}]+)\}\}", rep, text)


def main():
    res = os.path.join(ROOT, "results")
    nums = compute_numbers(res)
    json.dump(nums, open(os.path.join(HERE, "build", "numbers_used.json"), "w"), indent=1)
    parts = []
    for s in SECTIONS:
        p = os.path.join(HERE, "sections", s)
        if os.path.exists(p):
            parts.append(fill(open(p, encoding="utf8").read(), nums))
    md = "\n\n".join(parts)
    # abstract word count (journal limit 150-250)
    m = re.search(r"\*\*Abstract\*\*(.*?)\*\*Keywords\*\*", md, re.S)
    if m:
        words = len(re.sub(r"\$[^$]*\$", "x", m.group(1)).split())
        print("abstract words:", words)
        if not 150 <= words <= 250:
            print("WARNING: abstract outside 150-250 words")
    out_md = os.path.join(HERE, "build", "manuscript.md")
    open(out_md, "w", encoding="utf8").write(md)
    figs = os.path.join(res, "figures")
    docx = os.path.join(HERE, "Final_Manuscript.docx")
    fmt = "markdown+tex_math_dollars+pipe_tables+implicit_figures"
    subprocess.run(["pandoc", out_md, "-o", docx, "--number-sections", "--reference-doc",
                    os.path.join(HERE, "build", "reference.docx"), "--resource-path", f"{figs}:{HERE}", "-f", fmt],
                   check=True)
    # PDF for review: pandoc -> standalone HTML with MathML -> headless Chromium (LibreOffice drops OMML maths)
    html = os.path.join(HERE, "build", "manuscript.html")
    subprocess.run(["pandoc", out_md, "-s", "--mathml", "--number-sections", "--embed-resources", "-f", fmt,
                    "--css", os.path.join(HERE, "build", "print.css"), "--resource-path", f"{figs}:{HERE}",
                    "--metadata", "lang=en", "-o", html], check=True)
    chrome = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.join(HERE, 'Final_Manuscript.pdf')}", "file://" + html],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("built", docx)


if __name__ == "__main__":
    main()
