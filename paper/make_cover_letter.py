"""Fill the cover-letter template from the generated macros and write DOCX and PDF."""
import json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
idx = {v: k for k, v in json.load(open(os.path.join(HERE, "tables", "macro_index.json"))).items()}
vals = {}
for m in re.finditer(r"\\newcommand\{\\(N[A-Za-z]+)\}\{(.*)\}  %", open(os.path.join(HERE, "tables", "macros.tex")).read()):
    vals[m.group(1)] = m.group(2)
plain = lambda s: (s.replace(r"\ensuremath{-}", "−").replace(r"\%", "%").replace("--", "–")
                   .replace(r"\ensuremath{<}", "<"))
t = open(os.path.join(HERE, "cover_letter_template.md"), encoding="utf8").read()
t = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", lambda m: plain(vals[idx[m.group(1)]]), t)
md = os.path.join(HERE, "cover_letter.md")
open(md, "w", encoding="utf8").write(t)
subprocess.run(["pandoc", md, "-o", os.path.join(HERE, "Cover_Letter.docx")], check=True)
subprocess.run(["pandoc", md, "-o", os.path.join(HERE, "Cover_Letter.pdf"), "--pdf-engine=pdflatex"], check=True)
print("cover letter written")
