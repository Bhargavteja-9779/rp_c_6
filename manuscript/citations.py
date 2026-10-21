"""Convert author-year citations (Springer style) to numbered citations [n] in order of first
appearance (Elsevier numbered style), and renumber the reference list accordingly."""
import re


def _label(entry):
    m = re.match(r"(.+?)\s\((\d{4}[ab]?)\)", entry)
    authors, year = m.group(1), m.group(2)
    parts = [a.strip() for a in authors.split(",") if a.strip() and a.strip() != "et al"]
    sur = [p.rsplit(" ", 1)[0] if " " in p else p for p in parts]
    many = len(parts) > 2 or "et al" in authors
    if many:
        lab = f"{sur[0]} et al."
    elif len(sur) == 2:
        lab = f"{sur[0]} and {sur[1]}"
    else:
        lab = sur[0]
    return lab, year


def _fmt(nums):
    nums = sorted(set(nums))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(f"{nums[i]}–{nums[j]}" if j - i >= 2 else ", ".join(map(str, nums[i:j + 1])))
        i = j + 1
    return "[" + ", ".join(out) + "]"


def to_numbered(body, refs_block):
    entries = [e.strip() for e in refs_block.strip().split("\n\n") if e.strip()]
    labels = [_label(e) for e in entries]
    # first-appearance order: scan for both "Label Year" and "Label (Year)"
    pos = {}
    for i, (lab, yr) in enumerate(labels):
        pats = [re.escape(f"{lab} {yr}"), re.escape(f"{lab} ({yr})")]
        hits = [m.start() for p in pats for m in re.finditer(p + r"(?![0-9a-z])", body)]
        if hits:
            pos[i] = min(hits)
    order = sorted(pos, key=pos.get)
    num = {i: k + 1 for k, i in enumerate(order)}
    # narrative form first: "Lei et al. (2018)" -> "Lei et al. [n]"
    for i, (lab, yr) in enumerate(labels):
        if i in num:
            body = re.sub(re.escape(f"{lab} ({yr})") + r"(?![0-9a-z])", f"{lab} [{num[i]}]", body)
    # parenthetical tokens
    for i, (lab, yr) in sorted(enumerate(labels), key=lambda t: -len(t[1][0])):
        if i in num:
            body = re.sub(re.escape(f"{lab} {yr}") + r"(?![0-9a-z])", f"⟦{num[i]}⟧", body)

    def group(m):
        inner = m.group(1)
        nums = [int(x) for x in re.findall(r"⟦(\d+)⟧", inner)]
        if not nums:
            return m.group(0)
        rest = re.sub(r"⟦\d+⟧", "", inner)
        rest_clean = re.sub(r"[;,\s]+", " ", rest).strip()
        if not rest_clean:
            return _fmt(nums)
        if "see also" in rest:
            return "(" + re.sub(r"⟦(\d+)⟧", r"[\1]", inner) + ")"
        return f"({rest_clean}) " + _fmt(nums)
    body = re.sub(r"\(([^()]*⟦\d+⟧[^()]*)\)", group, body)
    body = re.sub(r"⟦(\d+)⟧", r"[\1]", body)
    uncited = [entries[i][:60] for i in range(len(entries)) if i not in num]
    new_refs = "\n\n".join(f"[{num[i]}] {entries[i]}" for i in order)
    leftover = re.findall(r"\b[A-Z][a-zé]+ (?:et al\. )?\(?(?:19|20)\d\d[ab]?\)?", body)
    return body, new_refs, uncited, leftover
