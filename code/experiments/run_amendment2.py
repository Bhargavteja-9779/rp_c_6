"""Amendment 2 runs: remedy comparison (applications), SCP-rand for wave 1, and wave 2 (UCI) when selected.
Usage: python experiments/run_amendment2.py remedies|tiebreak_w1|wave2"""
import json, os, sys
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp import experiments as E

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
R = os.path.join(ROOT, "results", "reinforcement")
cfg = json.load(open(os.path.join(ROOT, "code", "configs", "default.json")))
cfg["cache_dir"] = os.path.join(ROOT, "data_cache")


def job(args):
    fn, did, task, c, out = args
    try:
        return did, getattr(E, fn)(did, task, c, out)
    except Exception as e:
        return did, "ERROR " + repr(e)[:300]


def main(stage):
    if stage == "remedies":
        jobs = [("run_remedies", d, t, cfg, os.path.join(R, "remedies")) for d, t in cfg["remedy_ids"]]
    elif stage == "tiebreak_w1":
        c = dict(cfg, tie_break=True, tie_break_only=True, prosp_prefix="tb")
        sel = json.load(open(os.path.join(R, "prospective_selection.json")))
        jobs = [("run_prospective", x["data_id"], x["task"], c, os.path.join(R, "tiebreak_w1")) for x in sel["included"]]
    elif stage == "wave2":
        c = dict(cfg, tie_break=True, prosp_prefix="w2")
        sel = json.load(open(os.path.join(R, "prospective_selection_w2.json")))
        jobs = [("run_prospective", x["data_id"], x["task"], c, os.path.join(R, "prospective_w2")) for x in sel["included"]]
    with ProcessPoolExecutor(int(os.environ.get("WORKERS", 4))) as ex:
        for r in ex.map(job, jobs):
            print(*r, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
