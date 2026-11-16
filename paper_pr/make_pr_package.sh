#!/usr/bin/env bash
# Assemble the Pattern Recognition resubmission package (PR-D-26-16249) from a fresh, checked build.
set -euo pipefail
cd "$(dirname "$0")"
./build_pr.sh >/dev/null
OUT=../submission/PR_Resubmission; rm -rf "$OUT" "$OUT.zip"; mkdir -p "$OUT"
cp main_pr.pdf "$OUT/Manuscript.pdf"
cp supplement_pr.pdf "$OUT/Supplementary_Material.pdf"
# single-folder LaTeX source; test-compiled in a throwaway copy so the packaged files stay pristine
SRC=$(mktemp -d); python3 tools/flatten.py "$SRC/latex_source" >/dev/null
cp -r "$SRC/latex_source" "$SRC/test"
( cd "$SRC/test"
  for f in main_pr supplement_pr; do for i in 1 2 3; do pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error $f >/dev/null; done; done
  if grep -q "undefined\|Overfull" main_pr.log supplement_pr.log; then echo "flattened source has warnings"; exit 1; fi )
for f in main_pr supplement_pr; do
  cmp <(pdftotext $f.pdf -) <(pdftotext "$SRC/test/$f.pdf" -) || { echo "flattened $f differs from build"; exit 1; }
done
echo "flattened LaTeX source compiles stand-alone and matches the build"
( cd "$SRC" && zip -qr LaTeX_Source.zip latex_source ) && mv "$SRC/LaTeX_Source.zip" "$OUT/"
rm -rf "$SRC"
pandoc docs/highlights.md -o "$OUT/Highlights.docx"
pandoc docs/response_to_editor.md -o "$OUT/Response_to_Editor.docx"
pandoc docs/response_to_editor.md -o "$OUT/Response_to_Editor.pdf" -V geometry:margin=2.5cm -V fontsize=11pt
cp docs/README_resubmission.md "$OUT/README.md"
( cd ../submission && zip -qr PR_Resubmission.zip PR_Resubmission )
ls -la "$OUT"; echo "package: submission/PR_Resubmission.zip"
