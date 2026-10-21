"""Single entry point.

    python run_all.py --mode quick            # pipeline check on 3 small datasets (NOT evidence)
    python run_all.py --mode full             # all stages of the pre-registered protocol
    python run_all.py --mode full --stage main|inject|capacity|analyze

Stages: main (Experiments A-C, E, exploratory distance analysis), inject (D), capacity (F),
analyze (statistics, figures, tables). Raw outputs are written per dataset, so interrupted runs
resume where they stopped.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "src"))

from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402

QUICK_IDS = {"classification": [1067, 1464], "regression": [44956]}


def _env_record(path):
    import lightgbm, numpy, pandas, scipy, sklearn
    rec = {"python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
           "cpu_count": os.cpu_count(), "numpy": numpy.__version__, "pandas": pandas.__version__,
           "scipy": scipy.__version__, "sklearn": sklearn.__version__, "lightgbm": lightgbm.__version__,
           "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    json.dump(rec, open(path, "w"), indent=1)


def _dataset_list(cfg, quick):
    from dupcp.data import EXCLUDED_IMAGE_IDS, SUITES, suite_data_ids
    if quick:
        return [(t, i) for t, ids in QUICK_IDS.items() for i in ids]
    lst_path = os.path.join(ROOT, "results", "dataset_list.json")
    if os.path.exists(lst_path):
        return [tuple(x) for x in json.load(open(lst_path))]
    out = []
    for task, sid in SUITES.items():
        for i in suite_data_ids(sid):
            if i not in EXCLUDED_IMAGE_IDS:
                out.append((task, i))
    os.makedirs(os.path.dirname(lst_path), exist_ok=True)
    json.dump(out, open(lst_path, "w"))
    return out


def _run_pool(fn, jobs, cfg, out_dir, workers, log):
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn, i, t, cfg, out_dir): (t, i) for t, i in jobs}
        for f in as_completed(futs):
            t, i = futs[f]
            try:
                msg = f.result()
            except Exception as e:
                msg = f"FAILED {e!r}"
            line = f"{time.strftime('%H:%M:%S')} {fn.__name__} {t} {i}: {msg}"
            print(line, flush=True)
            log.write(line + "\n")
            log.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--stage", choices=["all", "main", "inject", "capacity", "external", "normalized", "neardup", "prospective", "analyze"], default="all")
    ap.add_argument("--config", default=os.path.join(HERE, "configs", "default.json"))
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    cfg = json.load(open(args.config))
    quick = args.mode == "quick"
    if quick:
        cfg.update(seeds=[0, 1], models=["logreg", "rf"], alphas=[0.1], inject_rates=[0.0, 0.5],
                   inject_seeds=[0], inject_models=["rf"], capacity_seeds=[0])
    cfg["cache_dir"] = os.path.join(ROOT, "data_cache")
    res = os.path.join(ROOT, "results_quick" if quick else "results")
    raw = os.path.join(res, "raw")
    os.makedirs(os.path.join(res, "logs"), exist_ok=True)
    _env_record(os.path.join(res, "logs", "environment.json"))
    json.dump(cfg, open(os.path.join(res, "logs", "config_used.json"), "w"), indent=1)
    workers = args.workers or cfg.get("workers", 4)
    from dupcp import experiments as E
    jobs = _dataset_list(cfg, quick)
    log = open(os.path.join(res, "logs", "run.log"), "a")

    # preload sequentially (network) so workers only read the local cache
    from dupcp.data import load_dataset
    for t, i in jobs:
        try:
            load_dataset(i, t, cfg["cache_dir"])
        except Exception as e:
            log.write(f"LOAD FAILED {t} {i} {e!r}\n")
            print("LOAD FAILED", t, i, e, flush=True)

    if args.stage in ("all", "main"):
        # largest first for load balancing
        from dupcp.data import load_dataset as ld
        sizes = {}
        for t, i in jobs:
            try:
                d = ld(i, t, cfg["cache_dir"])
                sizes[(t, i)] = len(d["y"]) * max(1, d["X"].shape[1])
            except Exception:
                sizes[(t, i)] = -1
        main_jobs = sorted([j for j in jobs if sizes[j] >= 0], key=lambda j: -sizes[j])
        _run_pool(E.run_dataset, main_jobs, cfg, raw, workers, log)

    if args.stage in ("all", "external") and not quick:
        from dupcp.data import EXTERNAL_IDS
        ext = [("classification", i) for i in EXTERNAL_IDS]
        for t, i in ext:
            load_dataset(i, t, cfg["cache_dir"])
        _run_pool(E.run_dataset, ext, cfg, os.path.join(res, "external"), workers, log)

    if args.stage in ("all", "normalized") and not quick:
        import glob as _g
        dupreg = []
        for p in _g.glob(os.path.join(raw, "audit_regression_*.json")):
            a = json.load(open(p))
            if a["excess_row_frac"] > 0 and a["pred_exposure"] >= 0.01:
                dupreg.append(("regression", a["data_id"]))
        _run_pool(E.run_normalized, sorted(dupreg), cfg, os.path.join(res, "normalized"), workers, log)

    if args.stage in ("all", "prospective") and not quick:
        sel = json.load(open(os.path.join(res, "reinforcement", "prospective_selection.json")))
        pj = [(x["task"], x["data_id"]) for x in sel["included"]]
        _run_pool(E.run_prospective, pj, cfg, os.path.join(res, "reinforcement", "prospective"), workers, log)

    if args.stage in ("all", "neardup"):
        import glob as _g
        ids = sorted({(r.split("_")[1], int(r.split("_")[2].split(".")[0]))
                      for r in map(os.path.basename, _g.glob(os.path.join(res, "inject", "inject_*.csv")))})
        if quick:
            ids = ids[:1]
        _run_pool(E.run_neardup, ids, cfg, os.path.join(res, "reinforcement", "neardup"), workers, log)

    if args.stage in ("all", "inject", "capacity"):
        import glob
        audits = {}
        for p in glob.glob(os.path.join(raw, "audit_*.json")):
            a = json.load(open(p))
            audits[(a["task"], a["data_id"])] = a
        if args.stage in ("all", "inject"):
            clean = [j for j in jobs if j in audits and audits[j]["excess_row_frac"] == 0
                     and audits[j]["n_rows"] >= (200 if quick else 1000)]
            if quick:
                clean = [j for j in jobs if j in audits][:1]
            _run_pool(E.run_injection, clean, cfg, os.path.join(res, "inject"), workers, log)
        if args.stage in ("all", "capacity"):
            dup = [j for j in jobs if j in audits and audits[j]["pred_exposure"] >= cfg["capacity_min_exposure"]]
            if quick:
                dup = dup[:1]
            _run_pool(E.run_capacity, dup, cfg, os.path.join(res, "capacity"), workers, log)

    if args.stage in ("all", "analyze"):
        from dupcp import analysis
        analysis.run(res, cfg, quick=quick)
    log.close()


if __name__ == "__main__":
    main()
