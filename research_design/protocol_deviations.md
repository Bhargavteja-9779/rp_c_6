# Protocol deviations and post-hoc analyses

Freeze commit: `0e58bdd`. Everything below happened **after** the freeze and is disclosed in
the manuscript.

| # | When | What | Why | Effect on confirmatory results |
|---|---|---|---|---|
| 1 | Pipeline debugging, after the freeze but before full runs | `run_injection` / `run_capacity` now create their output directories (a bug fix found in quick mode) | Crash in quick mode | None |
| 2 | After the main results (primary H1 **not** supported at the median level) | Added **exploratory** analyses: (a) exposure strata π < 0.1, 0.1–0.3, ≥ 0.3; (b) the Proposition 1 decomposition of each dataset × learner gap into a seen-over-coverage term and a marginal term; (c) counts of dataset × learner pairs with gaps below −0.02 and −0.05; (d) Fig. 8 | To explain *where* the gap arises. The theory says exposure alone is not sufficient: seen rows must also be over-covered. These analyses test that consequence | None. All pre-registered tests are reported unchanged and the new analyses are labelled exploratory |

| 3 | After the main results | **Verification run** on solar_flare (OpenML 44966): 200 extra random splits (seeds 1000–1199), ridge and LightGBM, absolute-residual score, α = 0.1 (`code/experiments/verify_solar_flare.py`) | With 10 seeds, MCP novel coverage on this dataset was 0.84–0.88, apparently contradicting Proposition 3 | Confirms that it was sampling noise: MCP novel coverage 0.909 (95% CI 0.899–0.918) for LightGBM and 0.907 (0.896–0.917) for ridge; SCP novel coverage 0.78 and 0.77. Per-split SD ≈ 0.07 with about 36 novel calibration rows. Reported as a verification and a stated limitation (high split-to-split variability when novel calibration sets are small) |

No dataset, seed or learner was excluded after outcomes were seen. No hyperparameter was
changed.
