# Data-leakage audit of the experimental pipeline (Agents 7, 10, 14)

Duplicate-record leakage is the **object of study**, not a defect of the pipeline. Protocol R keeps
it on purpose, because it reproduces standard practice. The audit below covers every *other*
leakage path. Each check names the code location that enforces it.

| Leakage type | Risk in this study | Control | Where |
|---|---|---|---|
| Preprocessing leakage (scalers, imputers, encoders fitted on all data) | Would change scores for calibration and test rows | All transformers live inside a scikit-learn `Pipeline` fitted on training rows only | `models.make_model`, `models.fit_predict` |
| Distance-taxonomy leakage (Exp. E) | Bin edges computed from calibration *labels* would break Mondrian validity | Edges are leave-one-out NN distances **within the training set**; calibration/test distances use the training-fitted representation; labels never used | `experiments._distance_bins` |
| Novelty-taxonomy leakage | Taxonomy depending on calibration labels would break Proposition 3 | κ uses training **feature keys** only | `experiments.run_dataset` (`tr_keys`) |
| Label leakage via the key | The target in the key would make "seen" label-dependent | The key hashes features only | `data.row_keys` |
| Test-set reuse for tuning | Optimistic thresholds or hyperparameters | No tuning; fixed hyperparameters declared in advance; thresholds use calibration rows only | `configs/default.json`, `conformal.thresholds` |
| Early-stopping leakage (MLP) | — | scikit-learn's early stopping draws its validation subset from the **training** rows | `models.make_model` |
| Seed selection | Cherry-picking | Seeds 0–9 fixed in the protocol; all reported | `configs/default.json` |
| Subsampling leakage | Breaking duplicate structure, or selecting by outcome | Whole-group subsampling with fixed seed 2026, done before any split and independent of labels | `data.group_preserving_subsample` |
| Calibration/test overlap | — | The three partitions are disjoint by construction (unit-tested) | `splits.*`, `tests/test_core.py` |
| Group split correctness | Groups crossing partitions | Unit test asserts disjoint key sets | `tests/test_core.py::test_group_split_disjoint_groups` |
| Injection experiment (D) | Copies leaking from test into the "clean" baseline | Copies are appended *before* splitting, mirroring real duplication; the ρ = 0 condition is the clean baseline | `experiments.inject_duplicates` |

**Residual limitations.**
* Duplicates are detected by *exact* equality of the stored feature vector. Records duplicated
  with tiny numeric perturbations count as novel. That makes the duplicate analysis
  conservative; Exp. E addresses near-duplicates descriptively.
* OpenML's default feature set is used as given. If a dataset contains an undocumented ID-like
  column, true record duplication is hidden, and the measured exposure is a lower bound.
