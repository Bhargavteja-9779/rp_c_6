"""Label-free selection from the UCI ML Repository API. Written for Amendment 1 (not triggered);
used for validation wave 2 (Amendment 2), which also excludes overlap with wave 1."""
import contextlib, io, json, os, re, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.audit import audit
from dupcp.data import load_dataset

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, "data_cache")
OUT = os.path.join(ROOT, "results", "reinforcement", "prospective_selection_w2.json")


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def v1_signatures():
    sig, names = [], set()
    for sub in ("raw", "external"):
        for p in os.listdir(os.path.join(ROOT, "results", sub)):
            if p.startswith("audit_"):
                a = json.load(open(os.path.join(ROOT, "results", sub, p)))
                sig.append((a["n_raw"], a["n_features"]))
                names.add(norm(a["name"]))
    # wave 1 (fresh OpenML set): names and size signatures of the included data sets
    w1 = json.load(open(os.path.join(ROOT, "results", "reinforcement", "prospective_selection.json")))
    for x in w1["included"]:
        names.add(norm(re.sub(r"(_v\d+|\(\d+\))$", "", x["name"])))
        nf = len(pd.read_parquet(os.path.join(CACHE, f"{x['data_id']}.parquet")).columns) - 1
        sig.append((x["n_raw"], nf))
    return sig, names


def main():
    from ucimlrepo import fetch_ucirepo, list_available_datasets
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        list_available_datasets()
    listing = []
    for line in buf.getvalue().splitlines():
        m = re.match(r"^(.*\S)\s+(\d+)\s*$", line)
        if m and not line.startswith("Dataset Name"):
            listing.append((m.group(1), int(m.group(2))))
    sig, names = v1_signatures()
    included, log, pool_names = [], [], set()
    for name, uid in sorted(listing, key=lambda t: t[1]):
        try:
            _process(name, uid, names, pool_names, sig, included, log, fetch_ucirepo)
        except Exception as e:
            log.append({"data_id": f"uci{uid}", "name": name, "uci_id": uid, "excluded": f"parse failed: {e!r}"[:200]})
    json.dump({"date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "source": "UCI (amendment 2, wave 2)",
               "pool_size": len(listing), "listing": listing, "included": included, "excluded": log},
              open(OUT, "w"), indent=1)
    print("included", len(included), "of", len(listing))


def _process(name, uid, names, pool_names, sig, included, log, fetch_ucirepo):
    if True:
        rec = {"data_id": f"uci{uid}", "name": name, "uci_id": uid}
        if norm(name) in names:
            log.append({**rec, "excluded": "name matches v1 or wave 1"}); return
        if norm(name) in pool_names:
            log.append({**rec, "excluded": "same name already in pool (lower UCI id kept)"}); return
        pool_names.add(norm(name))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                ds = fetch_ucirepo(id=uid)
        except Exception as e:
            log.append({**rec, "excluded": f"fetch failed: {e!r}"[:200]}); return
        X, Y = ds.data.features, ds.data.targets
        meta = ds.metadata
        tasks = " ".join(meta.get("tasks") or []) if isinstance(meta.get("tasks"), list) else str(meta.get("tasks"))
        if Y is None or X is None or Y.shape[1] != 1:
            log.append({**rec, "excluded": "not exactly one target"}); return
        task = "classification" if "Classification" in tasks else ("regression" if "Regression" in tasks else None)
        if task is None:
            log.append({**rec, "excluded": f"task {tasks}"}); return
        n, p_ = X.shape
        if not (300 <= n <= 5_000_000) or p_ > 2000:
            log.append({**rec, "excluded": "size limits"}); return
        if any(abs(n - a) <= 0.02 * a and abs(p_ - b) <= 1 for a, b in sig):
            log.append({**rec, "excluded": "size signature matches a v1 or wave-1 data set (conservative overlap rule)"}); return
        y = Y.iloc[:, 0]
        if task == "regression" and not pd.api.types.is_numeric_dtype(y):
            log.append({**rec, "excluded": "non-numeric regression target"}); return
        df = X.copy()
        cols, seen_c = [], {}
        for c in map(str, df.columns):  # some UCI files repeat column names; make them unique (parsing only)
            seen_c[c] = seen_c.get(c, 0) + 1
            cols.append(c if seen_c[c] == 1 else f"{c}__{seen_c[c]}")
        df.columns = cols
        df["__target__"] = y.values
        df.to_parquet(os.path.join(CACHE, f"uci{uid}.parquet"))
        json.dump({"name": name, "version": None, "target": str(Y.columns[0]), "source": "UCI"},
                  open(os.path.join(CACHE, f"uci{uid}.json"), "w"))
        try:
            d = load_dataset(f"uci{uid}", task, CACHE, rule="v2")
        except Exception as e:
            log.append({**rec, "excluded": f"parse failed: {e!r}"[:200]}); return
        a = audit(d["keys"], d["y"], task)
        rec.update(task=task, n_raw=d["n_raw"], n_rows=a["n_rows"], subsampled=d["subsampled"],
                   pred_exposure=a["pred_exposure"], dup_row_frac=a["dup_row_frac"])
        if a["pred_exposure"] >= 0.01:
            rec["included"] = True; included.append(rec)
        else:
            log.append({**rec, "excluded": "predicted exposure < 0.01"})
        print(uid, name, task, n, round(a["pred_exposure"], 3), flush=True)


if __name__ == "__main__":
    main()
