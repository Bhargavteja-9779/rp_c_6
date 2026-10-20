"""Crossref bibliographic search (fallback when OpenAlex/Semantic Scholar rate-limit).
Usage: python cr_search.py "query" [n] [from_year]"""
import json, sys, time, urllib.parse, urllib.request

q = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
fy = sys.argv[3] if len(sys.argv) > 3 else "2005"
url = (f"https://api.crossref.org/works?query.bibliographic={urllib.parse.quote(q)}&rows={n}"
       f"&filter=from-pub-date:{fy}-01-01&select=DOI,title,container-title,issued,is-referenced-by-count,type"
       f"&mailto=bhargavteja5098171@gmail.com")
for a in range(4):
    try:
        d = json.load(urllib.request.urlopen(url, timeout=60))
        break
    except Exception:
        time.sleep(3 * (a + 1))
else:
    print("FAILED", q)
    sys.exit()
for w in d["message"]["items"]:
    y = (w.get("issued", {}).get("date-parts") or [[None]])[0][0]
    print(y, w.get("is-referenced-by-count"), "|", (w.get("title") or [""])[0][:115], "|",
          (w.get("container-title") or [""])[0][:40], "|", w["DOI"])
