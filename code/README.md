# dupcp: duplicate records and conformal coverage on novel records

Code for the paper "Seen or new? Duplicate records, conformal coverage on novel inputs, and a
novelty-conditional remedy for tabular benchmarks".

## Requirements

Python ≥ 3.11 (tested with 3.13.16 on Linux x86-64, 4 CPU cores, no GPU) and the pinned packages
in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Internet access to `openml.org` is needed on the first run, to download the 103 public datasets.
They are cached in `../data_cache/`.

## Reproduce

```bash
python -m pytest -q tests                      # 11 unit tests (theory checks included)
python run_all.py --mode quick                 # pipeline smoke test, 3 datasets (NOT evidence)
python run_all.py --mode full --stage main     # Experiments A-C, E  (~2 h on 4 cores)
python run_all.py --mode full --stage inject   # Experiment D        (~1 h)
python run_all.py --mode full --stage capacity # Experiment F        (~1 h)
python run_all.py --mode full --stage analyze  # statistics, tables, figures (~2 min)
python experiments/verify_solar_flare.py       # post hoc verification run (~10 min)
python ../manuscript/build_manuscript.py       # manuscript DOCX/PDF from results (needs pandoc, LibreOffice)
```

All stages resume from per-dataset files. Outputs go to `../results/`:

| Path | Content |
|---|---|
| `raw/{task}_{id}.csv` | one row per dataset × split × protocol × learner × score × α × method |
| `raw/calib_*.csv`, `raw/dist_*.csv`, `raw/audit_*.json` | calibration metrics, distance-bin coverage, duplicate audit |
| `inject/`, `capacity/` | Experiments D and F |
| `tables/` | every table in the paper (T1–T8, X1–X2) as CSV |
| `statistics.json` | every test statistic and p-value |
| `figures/` | Fig1–Fig8 as PNG, EPS and TIFF |
| `logs/` | environment, configuration and run logs |

## Layout

```
src/dupcp/data.py         OpenML loading, record keys, group-preserving subsampling
src/dupcp/audit.py        label-free duplicate audit, exposure formula (Prop. 2)
src/dupcp/splits.py       random (R) and group-aware (G) splits
src/dupcp/models.py       learners; preprocessing fitted on training rows only
src/dupcp/conformal.py    LAC / randomized APS scores, split and Mondrian thresholds
src/dupcp/metrics.py      ECE and size-matched ECE
src/dupcp/experiments.py  experiment drivers (main grid, injection, capacity)
src/dupcp/analysis.py     pre-registered statistical analysis + labelled exploratory analyses
src/dupcp/figures.py      figures
configs/default.json      pre-registered configuration
```

The pre-registered protocol is `../research_design/experimental_protocol.md`; deviations are
listed in `../research_design/protocol_deviations.md`.
