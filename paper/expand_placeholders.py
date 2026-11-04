"""Replace {{key}} placeholders in paper/sections/*.tex by the generated macros (\\NKey{}).
{{key|w}} gives the word form for counts below ten. Unknown keys stop the script."""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
idx = {v: k for k, v in json.load(open(os.path.join(HERE, "tables", "macro_index.json"))).items()}
macros = open(os.path.join(HERE, "tables", "macros.tex")).read()
bad = []


def rep(m):
    key, word = m.group(1), m.group(2)
    if key not in idx:
        bad.append(key)
        return m.group(0)
    name = idx[key] + ("W" if word else "")
    if "\\" + name + "}" not in macros:
        bad.append(key + "|w")
    return "\\" + name + "{}"


for f in glob.glob(os.path.join(HERE, "sections", "*.tex")) + glob.glob(os.path.join(HERE, "supplement", "*.tex")):
    s = open(f).read()
    s2 = re.sub(r"\{\{([A-Za-z0-9_]+)(\|w)?\}\}", rep, s)
    if s2 != s:
        open(f, "w").write(s2)
if bad:
    sys.exit("unknown keys: " + ", ".join(sorted(set(bad))))
print("placeholders expanded")
