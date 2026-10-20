"""Estimate observed submission(received)->acceptance intervals for journals
from Crossref 'assertion' metadata (deposited by Springer Nature, T&F, others).

Evidence level 3 in the project's hierarchy: an observed sample of recently
published articles, NOT a guarantee of future turnaround. Articles that were
desk-rejected or rejected never appear, so this is a survivorship-biased
estimate of the time-to-acceptance among accepted papers.
"""
import json, sys, time, urllib.request, urllib.parse, statistics, datetime as dt
import re

MAILTO = "bhargavteja5098171@gmail.com"

def parse_date(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None

def fetch(issn, from_date, until_date, max_items=600):
    items, cursor = [], "*"
    while len(items) < max_items:
        q = {
            "filter": f"from-pub-date:{from_date},until-pub-date:{until_date},type:journal-article",
            "rows": "200", "cursor": cursor, "select": "DOI,assertion,title",
            "mailto": MAILTO,
        }
        url = f"https://api.crossref.org/journals/{issn}/works?" + urllib.parse.urlencode(q)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    d = json.load(r)
                break
            except Exception as e:
                time.sleep(2 ** (attempt + 1))
        else:
            break
        batch = d["message"]["items"]
        if not batch:
            break
        items += batch
        cursor = d["message"].get("next-cursor")
        if not cursor:
            break
    return items[:max_items]

def intervals(items):
    out = []
    for it in items:
        rec = acc = None
        for a in it.get("assertion", []) or []:
            n = (a.get("name") or "").lower()
            v = a.get("value") or ""
            if n == "received" and rec is None:
                rec = parse_date(v)
            elif n == "accepted" and acc is None:
                acc = parse_date(v)
        if rec and acc and acc >= rec:
            out.append({"doi": it["DOI"], "received": str(rec), "accepted": str(acc),
                        "days": (acc - rec).days})
    return out

def summarize(days):
    days = sorted(days)
    n = len(days)
    if n == 0:
        return {"n": 0}
    q = lambda p: days[min(n - 1, int(round(p * (n - 1))))]
    return {"n": n, "median": statistics.median(days), "p25": q(0.25), "p75": q(0.75),
            "p90": q(0.9), "mean": round(statistics.mean(days), 1),
            "share_le_72": round(sum(d <= 72 for d in days) / n, 3)}

if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    report = {"verified_on": str(dt.date.today()), "window": cfg["window"], "journals": {}}
    for j in cfg["journals"]:
        items = fetch(j["issn"], *cfg["window"], max_items=cfg.get("max_items", 600))
        iv = intervals(items)
        s = summarize([x["days"] for x in iv])
        s.update({"articles_retrieved": len(items), "issn": j["issn"], "publisher": j["publisher"]})
        report["journals"][j["name"]] = s
        json.dump(iv, open(f"{out_dir}/raw_{j['issn']}.json", "w"), indent=0)
        print(j["name"], s, flush=True)
    json.dump(report, open(f"{out_dir}/timeline_summary.json", "w"), indent=2)
