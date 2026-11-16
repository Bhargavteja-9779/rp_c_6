#!/usr/bin/env bash
# Build the Pattern Recognition manuscript and supplement, then check the journal's format requirements.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf tables && cp -r ../paper/tables tables          # single source of all numbers
python3 expand_placeholders.py >/dev/null
python3 tools/make_data_links.py >/dev/null          # supplementary link list, from the study records
grep -v "& LGBM &" tables/tab_cases.tex > tables/tab_cases_rf.tex   # main text: random forest rows
TEX="pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error"
$TEX supplement_pr.tex >/dev/null; $TEX main_pr.tex >/dev/null; bibtex main_pr >/dev/null
$TEX supplement_pr.tex >/dev/null; $TEX main_pr.tex >/dev/null; $TEX main_pr.tex >/dev/null; $TEX supplement_pr.tex >/dev/null
echo "== Checks (Pattern Recognition requirements) =="
fail=0
for doc in main_pr supplement_pr; do
  oh=$(grep -c "^Overfull \\\\hbox" $doc.log || true); ov=$(grep -c "^Overfull \\\\vbox" $doc.log || true)
  ur=$(grep -c "Reference .* undefined\|There were undefined references" $doc.log || true)
  uc=$(grep -c "Citation .* undefined" $doc.log || true)
  pages=$(pdfinfo $doc.pdf | awk '/^Pages/{print $2}'); size=$(pdfinfo $doc.pdf | awk -F': *' '/^Page size/{print $2}')
  leak=$(pdftotext $doc.pdf - | grep -c '\\N[A-Z]\|{{' || true)
  echo "$doc: pages=$pages size=[$size] overfull_h=$oh overfull_v=$ov undefined_refs=$ur undefined_cites=$uc macro_leaks=$leak"
  [ "$oh" = 0 ] && [ "$ov" = 0 ] && [ "$ur" = 0 ] && [ "$uc" = 0 ] && [ "$leak" = 0 ] || fail=1
done
pages=$(pdfinfo main_pr.pdf | awk '/^Pages/{print $2}'); [ "$pages" -le 35 ] || { echo "PAGE LIMIT EXCEEDED"; fail=1; }
n_q=$(pdftotext main_pr.pdf - | grep -c "author?" || true); [ "$n_q" -eq 0 ] || { echo "UNRESOLVED (author?) CITATIONS: $n_q"; fail=1; }
set +e
python3 - <<'PY'
import re, subprocess
t = subprocess.run(["pdftotext", "main_pr.pdf", "-"], capture_output=True, text=True).stdout
abs_ = t.split("Abstract", 1)[1].split("Keywords", 1)[0]
print("abstract words:", len(abs_.split()), "(max 250)")
title = re.search(r"\\title\{(.*?)\}", open("main_pr.tex").read()).group(1)
print("title words:", len(title.split()), "(max 15)")
refs = len(re.findall(r"\\bibitem", open("main_pr.bbl").read()))
print("references:", refs, "(35-55)")
ok = len(abs_.split()) <= 250 and len(title.split()) <= 15 and 35 <= refs <= 55
raise SystemExit(0 if ok else 1)
PY
[ $? -eq 0 ] || fail=1
[ "$fail" = 0 ] && echo "ALL CHECKS PASSED"
exit $fail
