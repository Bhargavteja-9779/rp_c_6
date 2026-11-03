"""E13 (post hoc, D15d): run time and peak memory of the check and of the fix, measured with the
covercheck tool on the stated hardware. Model fitting is timed separately: it is the same for every
calibration method and dominates the total.

Data: three application/fresh data sets at their analysed size (30,000 rows after subsampling where
applicable): KDD Cup'99 (1113), mc1 (1056), Skin Segmentation (UCI 229). Five repetitions; median.
"""
import json, os, platform, sys, time, tracemalloc
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tool", "src"))
sys.path.insert(0, os.path.join(ROOT, "code", "src"))
from covercheck import SeenNewConformal, check
from covercheck.cli import default_model
from dupcp.data import load_dataset

OUT = os.path.join(ROOT, "results", "e13_cost")
SETS = [(1113, "KDD Cup'99"), (1056, "mc1"), ("uci229", "Skin Segmentation")]


def timed(fn, reps=5):
    ts, peaks = [], []
    for _ in range(reps):
        tracemalloc.start()
        t0 = time.perf_counter()
        out = fn()
        ts.append(time.perf_counter() - t0)
        peaks.append(tracemalloc.get_traced_memory()[1])
        tracemalloc.stop()
    return float(np.median(ts)), float(np.median(peaks)) / 2 ** 20, out


def cpu_name():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for did, name in SETS:
        rule = "v2" if isinstance(did, str) else "v1"
        d = load_dataset(did, "classification", os.path.join(ROOT, "data_cache"), rule=rule)
        X, y = d["X"].reset_index(drop=True), d["y"]
        n = len(y)
        perm = np.random.default_rng(0).permutation(n)
        tr, ca, te = perm[:int(0.6 * n)], perm[int(0.6 * n):int(0.8 * n)], perm[int(0.8 * n):]
        t_check, m_check, _ = timed(lambda: check(X, y))
        est = default_model("classification", X)
        t0 = time.perf_counter()
        base = SeenNewConformal(est, "classification", 0.1, mode="exact").fit(X.iloc[tr], y[tr])
        t_fit = time.perf_counter() - t0
        res = dict(data=name, rows=n, features=X.shape[1], check_s=t_check, check_peak_mb=m_check, fit_s=t_fit)
        for mode in ("standard", "exact", "distance"):
            m = SeenNewConformal(base.estimator, "classification", 0.1, mode=mode)
            m._train_keys = base._train_keys
            if mode == "distance":
                m.fit_distance_index(X.iloc[tr])
            t_cal, mem_cal, _ = timed(lambda: m.calibrate(X.iloc[ca], y[ca]))
            t_pred, mem_pred, _ = timed(lambda: m.predict_set(X.iloc[te]))
            res.update({f"{mode}_calibrate_s": t_cal, f"{mode}_calibrate_peak_mb": mem_cal,
                        f"{mode}_predict_s": t_pred, f"{mode}_predict_peak_mb": mem_pred})
        rows.append(res)
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    hw = dict(cpu=cpu_name(), logical_cpus=os.cpu_count(),
              ram_gb=round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2 ** 30, 1),
              python=platform.python_version(), os=platform.platform())
    json.dump(dict(hardware=hw, rows=rows), open(os.path.join(OUT, "cost.json"), "w"), indent=1)
    print(hw)


if __name__ == "__main__":
    main()
