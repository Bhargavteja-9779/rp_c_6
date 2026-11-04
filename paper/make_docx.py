"""Word version of the manuscript: flatten main.tex, substitute the number macros, resolve cross-references
from the LaTeX .aux files, number the captions ("Fig. N", "Table N"), convert with pandoc (native Word
equations) and fix table widths with python-docx. Run after build.sh."""
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Main_Manuscript_Word.docx")


def read(p):
    return open(os.path.join(HERE, p), encoding="utf8").read()


def flatten(tex):
    def inc(m):
        name = m.group(1)
        if name.endswith("macros.tex"):
            return ""
        path = name if name.endswith(".tex") else name + ".tex"
        return flatten(read(path))
    tex = re.sub(r"\\input\{([^}]+)\}", inc, tex)
    return re.sub(r"\\tabinput\{([^}]+)\}", inc, tex)


def macros():
    out = {}
    for m in re.finditer(r"\\newcommand\{\\(N[A-Za-z]+)\}\{(.*)\}  %", read("tables/macros.tex")):
        out[m.group(1)] = m.group(2)
    return out


def labels(aux, prefix=""):
    out = {}
    for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", read(aux)):
        out[prefix + m.group(1)] = m.group(2)
    return out


def main():
    tex = flatten(read("main.tex"))
    tex = re.sub(r"\\newcommand\{\\(cmark|xmark|pp)\}\{[^\n]*\}\n", "", tex)
    tex = re.sub(r"\\makeatletter\\newcommand\\tabinput[^\n]*\n", "", tex)
    M = macros()
    tex = re.sub(r"\\(N[A-Za-z]+)(\{\})?", lambda m: M.get(m.group(1), m.group(0)), tex)
    L = labels("main.aux")
    L.update(labels("supplement.aux", "S-"))
    tex = re.sub(r"\\ref\{([^}]+)\}", lambda m: L.get(m.group(1), "??"), tex)
    # number captions: find the label inside each float and prefix the caption
    def number(env, word):
        def fix(m):
            body = m.group(0)
            lab = re.search(r"\\label\{([^}]+)\}", body)
            n = L.get(lab.group(1), "") if lab else ""
            return body.replace("\\caption{", f"\\caption{{\\textbf{{{word} {n}}} ", 1)
        return re.sub(r"\\begin\{" + env + r"\*?\}.*?\\end\{" + env + r"\*?\}", fix, tex, flags=re.S)
    tex = number("figure", "Fig.")
    tex = number("table", "Table")
    # Algorithm 1 as a numbered list (pandoc does not render algorithmic)
    def alg(m):
        body = m.group(0)
        cap = re.search(r"\\caption\{(.*?)\}\\label", body, re.S).group(1)
        steps = re.findall(r"\\(?:State|Require|Statex)\s*(.*)", body)
        items = "\n".join(f"\\item {s}" for s in steps)
        return f"\\paragraph{{Algorithm 1: {cap}}}\n\\begin{{enumerate}}\n{items}\n\\end{{enumerate}}"
    tex = re.sub(r"\\begin\{algorithm\}.*?\\end\{algorithm\}", alg, tex, flags=re.S)
    tex = re.sub(r"\\multicolumn\{(\d+)\}\{@\{\}l\}\{(.*?)\} \\\\", lambda m: m.group(2) + " &" * (int(m.group(1)) - 1) + r" \\", tex)
    tex = tex.replace(r"\addlinespace", "")
    for a, b in ((r"\ensuremath{-}", "−"), (r"\ensuremath{<}", "<"), (r"\ensuremath{>}", ">"), (r"\ensuremath{\to}", "→"),
                 (r"\ensuremath{\geq}", "≥"), (r"\ensuremath{\leq}", "≤"), (r"\ensuremath{\times}", "×"), (r"\ldots{}", "…")):
        tex = tex.replace(a, b)
    rep = [(r"\botrule", r"\bottomrule"), (r"\backmatter", ""), (r"\cmark", "✓"), (r"\xmark", "✗"),
           ("figures/fig_schematic.pdf", "figures/fig_schematic.png"), (".pdf}", ".png}"),
           (r"\begin{tabularx}{\textwidth}", r"\begin{tabular}"), (r"\end{tabularx}", r"\end{tabular}")]
    for a, b in rep:
        tex = tex.replace(a, b)
    tex = re.sub(r"(\\begin\{tabular\}\{[^}]*?)X", r"\1l", tex)
    tex = tex.replace("@{}Xccccccc@{}", "lccccccc").replace("@{}lXrlll@{}", "llrlll").replace("@{}lXXp{2.3cm}@{}", "llll")
    tex = re.sub(r"\\abstract\{(.*?)\}\n\n\\keywords\{(.*?)\}", r"\\begin{abstract}\1\\end{abstract}\n\n\\noindent\\textbf{Keywords:} \2",
                 tex, flags=re.S)
    tex = re.sub(r"\\bmhead\{([^}]*)\}", r"\\paragraph{\1}", tex)
    tex = re.sub(r"\\setlength\{\\tabcolsep\}\{[^}]*\}", "", tex)
    tex = re.sub(r"\\begin\{assumption\}\[([^]]*)\]\\label\{([^}]+)\}", lambda m: f"\\paragraph{{Assumption {L.get(m.group(2), '')} ({m.group(1)}).}}", tex)
    tex = tex.replace(r"\end{assumption}", "")
    tex = re.sub(r"\\begin\{proposition\}\[([^]]*)\]\\label\{([^}]+)\}", lambda m: f"\\paragraph{{Proposition {L.get(m.group(2), '')} ({m.group(1)}).}}", tex)
    tex = tex.replace(r"\end{proposition}", "")
    flat = os.path.join(HERE, "main_flat_for_word.tex")
    open(flat, "w", encoding="utf8").write(tex)
    subprocess.run(["pandoc", flat, "-f", "latex", "-o", OUT, "--citeproc", "--bibliography", os.path.join(HERE, "refs.bib"),
                    "--resource-path", HERE, "--number-sections"], check=True, cwd=HERE)
    # post-process: fixed table widths, centred
    from docx import Document
    from docx.shared import Cm
    d = Document(OUT)
    width = Cm(16)
    for t in d.tables:
        t.autofit = False
        n = len(t.columns)
        # column widths proportional to the longest cell text (capped), at least 1.3 cm each
        L = [min(max(len(r.cells[i].text) for r in t.rows), 45) + 4 for i in range(n)]
        widths = [max(width * l / sum(L), Cm(1.3)) for l in L]
        scale = width / sum(widths)
        widths = [w * scale for w in widths]
        for row in t.rows:
            for c, w in zip(row.cells, widths):
                c.width = int(w)
    d.save(OUT)
    xml = subprocess.run(["unzip", "-p", OUT, "word/document.xml"], capture_output=True, text=True).stdout
    print(f"tables: {len(d.tables)}, equations: {xml.count('<m:oMath>') + xml.count('<m:oMathPara>')}, "
          f"images: {xml.count('<pic:pic')}, unresolved refs: {tex.count('??')}, "
          f"leftover macros: {len(re.findall(r'[^a-z]N[A-Z][a-z]+[A-Z][A-Za-z]*\\{', tex))}")


if __name__ == "__main__":
    main()
