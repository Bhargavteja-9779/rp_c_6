"""Resolve DOIs on Crossref and record authoritative metadata (title, authors, year, venue)."""
import json, sys, time, urllib.request, urllib.parse
dois = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
out = {}
for doi in dois:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi) + "?mailto=bhargavteja5098171@gmail.com"
    for a in range(4):
        try:
            m = json.load(urllib.request.urlopen(url, timeout=60))["message"]; break
        except Exception as e:
            m = {"error": str(e)}; time.sleep(2 * (a + 1))
    if "error" in m:
        out[doi] = m; print("FAIL", doi, m["error"]); continue
    au = [f"{x.get('family','')}, {x.get('given','')}".strip(', ') for x in m.get("author", [])]
    yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    rec = {"title": (m.get("title") or [""])[0], "authors": au, "year": yr,
           "venue": (m.get("container-title") or [""])[0], "volume": m.get("volume"),
           "issue": m.get("issue"), "page": m.get("page") or m.get("article-number"), "type": m.get("type"),
           "publisher": m.get("publisher")}
    out[doi] = rec
    print(doi, "|", yr, "|", "; ".join(au[:3]) + (" et al." if len(au) > 3 else ""), "|", rec["title"][:90], "|", rec["venue"][:40], rec["volume"], rec["page"])
json.dump(out, open(sys.argv[2], "w"), indent=1)
