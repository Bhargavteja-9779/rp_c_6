"""Label-free selection of the prospective validation set (revised protocol, section 1).

Pool: OpenML studies 271, 269 (AutoML Benchmark) and 334-337 (Grinsztajn et al. 2022). Every
exclusion is recorded with its reason. Inclusion uses only feature keys (no labels, no models).
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.audit import audit
from dupcp.data import load_dataset

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, "data_cache")
OUT = os.path.join(ROOT, "results", "reinforcement", "prospective_selection.json")
STUDIES = {271: "classification", 269: "regression", 334: None, 335: None, 336: None, 337: None}


def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            err = e
            time.sleep(2 ** (i + 1))
    raise err


def norm(name):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"(_v\d+|\(\d+\))$", "", name.lower()))


def main():
    used = json.load(open(os.path.join(ROOT, "results", "dataset_list.json")))
    used_ids = {int(i) for _, i in used} | {1056, 1069, 1065, 1071, 1113}
    used_names = set()
    for p in os.listdir(os.path.join(ROOT, "results", "raw")) + os.listdir(os.path.join(ROOT, "results", "external")):
        if p.startswith("audit_"):
            src = "raw" if os.path.exists(os.path.join(ROOT, "results", "raw", p)) else "external"
            used_names.add(norm(json.load(open(os.path.join(ROOT, "results", src, p)))["name"]))
    cand, log = {}, []
    for sid, task in STUDIES.items():
        st = get(f"https://www.openml.org/api/v1/json/study/{sid}")["study"]
        for did in st["data"]["data_id"]:
            cand.setdefault(int(did), {"studies": [], "task_hint": task})["studies"].append(sid)
    included = []
    for did, info in sorted(cand.items()):
        rec = {"data_id": did, "studies": info["studies"]}
        if did in used_ids:
            log.append({**rec, "excluded": "id already used in v1"}); continue
        try:
            dd = get(f"https://www.openml.org/api/v1/json/data/{did}")["data_set_description"]
            q = {}
            for x in get(f"https://www.openml.org/api/v1/json/data/qualities/{did}")["data_qualities"]["quality"]:
                try:
                    q[x["name"]] = float(x["value"])
                except (TypeError, ValueError):  # some qualities are lists or empty; not needed here
                    pass
        except Exception as e:
            log.append({**rec, "excluded": f"metadata failed: {e!r}"[:200]}); continue
        name = dd["name"]; rec["name"] = name
        if norm(name) in used_names:
            log.append({**rec, "excluded": "name already used in v1"}); continue
        if q.get("NumberOfFeatures", 0) > 2000 or q.get("NumberOfInstances", 0) > 5_000_000:
            log.append({**rec, "excluded": "size limits"}); continue
        task = info["task_hint"]
        if task is None:  # Grinsztajn suites: infer from the default target's type
            nclass = q.get("NumberOfClasses", 0)
            task = "classification" if nclass and nclass > 0 else "regression"
        rec["task"] = task
        try:
            d = load_dataset(did, task, CACHE, rule="v2")
        except Exception as e:
            log.append({**rec, "excluded": f"download/parse failed: {e!r}"[:200]}); continue
        a = audit(d["keys"], d["y"], task)
        rec.update(n_raw=d["n_raw"], n_rows=a["n_rows"], subsampled=d["subsampled"],
                   pred_exposure=a["pred_exposure"], dup_row_frac=a["dup_row_frac"])
        if a["pred_exposure"] >= 0.01:
            rec["included"] = True; included.append(rec)
        else:
            log.append({**rec, "excluded": "predicted exposure < 0.01"})
        print(did, name, task, round(a["pred_exposure"], 3), flush=True)
    # Deviation 2 (label-free, fixed before any outcome was computed): the pool lists some data sets
    # under two ids (e.g. an AMLB and a Grinsztajn copy). Keep one per normalized name, the lowest id.
    keep, seen_names = [], set()
    for rec in sorted(included, key=lambda r: r["data_id"]):
        if norm(rec["name"]) in seen_names:
            log.append({**rec, "included": False, "excluded": "same data set already included under a lower id"})
        else:
            seen_names.add(norm(rec["name"])); keep.append(rec)
    included = keep
    json.dump({"date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "pool_size": len(cand),
               "included": included, "excluded": log}, open(OUT, "w"), indent=1)
    print("included", len(included), "of", len(cand))


if __name__ == "__main__":
    main()
