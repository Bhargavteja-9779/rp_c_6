"""Query OpenAlex (polite pool) and print year, citations, venue, DOI, title.
Usage: python oa_search.py "query" [n] [from_year]"""
import json, sys, time, urllib.parse, urllib.request
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
fy = sys.argv[3] if len(sys.argv) > 3 else None
flt = f"&filter=from_publication_date:{fy}-01-01" if fy else ""
url = (f"https://api.openalex.org/works?search={urllib.parse.quote(q)}&per-page={n}{flt}"
       f"&mailto=bhargavteja5098171@gmail.com")
for a in range(5):
    try:
        d = json.load(urllib.request.urlopen(url, timeout=60)); break
    except Exception as e:
        time.sleep(3 * (a + 1))
else:
    print("FAILED", q); sys.exit()
for w in d["results"]:
    v = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    print(w.get("publication_year"), w.get("cited_by_count"), "|", (w.get("title") or "")[:120], "|", v[:45], "|", (w.get("doi") or "").replace("https://doi.org/", ""))
