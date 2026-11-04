#!/usr/bin/env bash
# Build the manuscript and the supplement (cross-referenced with xr-hyper), then run the layout checks.
# Usage: ./build.sh            (from the paper/ folder)
# Requires pdflatex and bibtex (TeX Live). Shell escape is disabled.
set -euo pipefail
cd "$(dirname "$0")"
TEX="pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error"

$TEX supplement.tex >/dev/null
$TEX main.tex >/dev/null
bibtex main >/dev/null
$TEX supplement.tex >/dev/null
$TEX main.tex >/dev/null
$TEX main.tex >/dev/null
$TEX supplement.tex >/dev/null

echo "== Checks =="
fail=0
for doc in main supplement; do
  of=$(grep -c "^Overfull" $doc.log || true)
  ur=$(grep -c "Reference .* undefined\|There were undefined references" $doc.log || true)
  uc=$(grep -c "Citation .* undefined" $doc.log || true)
  pages=$(pdfinfo $doc.pdf 2>/dev/null | awk '/^Pages/{print $2}')
  leak=$(pdftotext $doc.pdf - 2>/dev/null | grep -c '\\N[A-Z]\|{{' || true)
  echo "$doc: pages=$pages overfull=$of undefined_refs=$ur undefined_cites=$uc macro_leaks=$leak"
  [ "$of" = 0 ] && [ "$ur" = 0 ] && [ "$uc" = 0 ] && [ "$leak" = 0 ] || fail=1
done
uf=$(grep -c "Warning--" main.blg || true)
echo "bibtex warnings: $uf"
exit $fail
