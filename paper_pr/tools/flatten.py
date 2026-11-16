"""Build a single-folder, single-file LaTeX source for Editorial Manager.

Inlines every \\input / \\tabinput, the .bbl bibliography, and resolves the
cross-document references (S- and M- prefixes from xr-hyper) to the literal
numbers in the other document's .aux, so the file compiles stand-alone.
Usage: python3 tools/flatten.py OUTDIR
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def labels(aux):
    lab = {}
    for line in open(os.path.join(HERE, aux), encoding="utf-8"):
        m = re.match(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", line)
        if m:
            lab[m.group(1)] = m.group(2)
    return lab


def inline(text, depth=0):
    def rep(m):
        name = m.group(2)
        path = os.path.join(HERE, name if name.endswith(".tex") else name + ".tex")
        body = open(path, encoding="utf-8").read()
        body = re.sub(r"(?m)^\s*%.*\n", "", body)
        return inline(body, depth + 1).rstrip("\n")
    return re.sub(r"\\(input|tabinput)\{?([A-Za-z0-9_/.\-]+?)\}?(?=[\s}]|$)", rep, text)


def resolve(text, prefix, lab):
    def rep(m):
        key = m.group(2)
        if key not in lab:
            raise SystemExit(f"unresolved cross-document label {prefix}{key}")
        val = lab[key]
        return f"({val})" if m.group(1) == "eqref" else val
    return re.sub(r"\\(ref|eqref)\{" + prefix + r"([^}]*)\}", rep, text)


def flatten(src, other_aux, prefix, bbl):
    text = open(os.path.join(HERE, src), encoding="utf-8").read()
    text = re.sub(r"\\makeatletter\\newcommand\\tabinput\[1\]\{\\@@input #1 \}\\makeatother\n", "", text)
    text = inline(text)
    text = re.sub(r"\\usepackage\{xr-hyper\}\n|\\externaldocument\[[SM]-\]\{[^}]*\}\n", "", text)
    text = resolve(text, prefix, labels(other_aux))
    if bbl:
        text = re.sub(r"\\bibliographystyle\{[^}]*\}\n\\bibliography\{[^}]*\}",
                      lambda _m: open(os.path.join(HERE, bbl), encoding="utf-8").read(), text)
    text = text.replace("{figures/", "{")
    return text


open(os.path.join(OUT, "main_pr.tex"), "w", encoding="utf-8").write(
    flatten("main_pr.tex", "supplement_pr.aux", "S-", "main_pr.bbl"))
open(os.path.join(OUT, "supplement_pr.tex"), "w", encoding="utf-8").write(
    flatten("supplement_pr.tex", "main_pr.aux", "M-", "supplement_pr.bbl" if os.path.exists(os.path.join(HERE, "supplement_pr.bbl")) else None))
for f in os.listdir(os.path.join(HERE, "figures")):
    if f.endswith(".pdf") or f == "fig_tool.png":
        shutil.copy(os.path.join(HERE, "figures", f), OUT)
print("flattened into", OUT)
