# Revised experimental protocol: reinforcement cycle (pre-specified)

**Freeze point:** the git commit that first adds this file. No reinforcement experiment
(U2–U4) had been run, and no prospective dataset had been downloaded, when it was written.
Everything in the v1 protocol stays as reported; this document adds to it.

## 1. Prospective validation set (U4)

* **Pool:** all datasets in OpenML studies 271 (AMLB classification), 269 (AMLB regression), 334,
  335, 336, 337 (Grinsztajn et al. 2022 suites).
* **Exclusions (applied in order, recorded):**
  1. OpenML data id already used in v1 (103 suite + 5 external datasets).
  2. Dataset *name* (case-insensitive, ignoring version suffixes) already used in v1, to avoid
     re-entering the same data under another id.
  3. More than 2,000 features, or more than 5,000,000 rows (download feasibility). Image
     datasets are excluded.
  4. The download or parse fails (recorded).
* **Subsampling:** to at most 30,000 rows; whole record groups, except when the largest group
  exceeds 6,000 rows (20% of the cap), in which case uniform row subsampling is used (the rule
  that was forced on KDD Cup'99 in v1, now stated in advance). Seed 2026.
* **Inclusion:** label-free predicted exposure π̄ ≥ 0.01 (the v1 DUP definition), computed after
  subsampling. Inclusion uses **no labels and no models**.
* **Learners:** RF (200 trees), LightGBM (300 trees), LR/ridge, as in v1. **Scores:** LAC
  (classification), |res| (regression), plus the normalized residual (regression; v1 definition).
  **α = 0.1.** **Seeds 0–19.** **Protocol R** (60/20/20 random split).
* **Methods:** SCP, MCP (exact-key seen/novel), PAC-MCP (δ = 0.1), DCP (six-bin
  distance-Mondrian, v1 definition), and for regression SCP and MCP with the normalized score.

## 2. Pre-specified quantities

* **π_P (label purity–adjusted exposure):** for each split, the share of test rows that (i) have
  ≥ 1 training row with an identical feature key and (ii) whose training copies **all** carry
  exactly the test row's label (classification) or target value (regression). Averaged over seeds.
* **Purity-adjusted bound:** g* = −α π_P/(1 − π_P) (−α if π_P ≥ 1 − α).
* **Exposure-only bound:** g_π = −α π/(1 − π).
* **Observed gap:** mean over seeds of (novel-row coverage − 0.9) under SCP.

## 3. Pre-specified tests (prospective set; unit = dataset)

* **P1 (discrimination).** Spearman ρ(g*, observed SCP gap) for RF with LAC or |res| (primary
  learner, pooled over tasks): one-sided test of ρ > 0. Secondary: the same for LightGBM and LR.
* **P2 (bound).** For RF, the share of datasets whose observed gap lies above g* − 0.02 (the bound
  holds up to noise). Hypothesis: ≥ 80%. Reported with an exact binomial 95% CI.
* **P3 (remedy).** Median MCP-R and PAC-MCP novel gaps: bootstrap 95% CI lower bound > −0.01 (RF,
  LightGBM, LR).
* **P4 (training-conditional).** Per dataset, the fraction of seeds with novel coverage below
  0.87, for MCP vs PAC-MCP: one-sided paired Wilcoxon test (PAC-MCP lower).
* **P5 (purity vs exposure).** Spearman ρ of g* vs ρ of g_π with the observed RF gap; the
  difference is reported with a dataset-bootstrap 95% CI (10,000 resamples).
* **Multiplicity:** Holm across the primary tests {P1 (RF), P3 (RF, MCP), P4}. Everything else is
  secondary.
* **Retrospective analysis (non-blind, labelled as such):** the same P1/P2/P5 quantities on the
  v1 suites (DUP), the external set and the injection experiment.

## 4. Near-duplicate injection (U3)

* **Datasets:** the 37 duplicate-free datasets of the v1 injection experiment (≥ 1,000 rows,
  randomly capped at 10,000 rows, v1 seed rule).
* **Design:** append jittered copies of a random 50% of rows (ρ = 0.5). Each numeric feature
  gets jitter N(0, (σ · sd_j)²), σ ∈ {0, 10⁻³, 10⁻², 10⁻¹}, where sd_j is the original feature's
  standard deviation. Categorical features and labels are copied unchanged. Seeds 0–2; RF and
  LightGBM; LAC or |res|; α = 0.1; protocol R.
* **Ground-truth novelty:** a test row is *truly new* if no training row descends from the same
  original record (source id tracked through the injection).
* **Methods:** SCP; MCP-exact (exact-key taxonomy); DCP (distance-Mondrian, v1 definition);
  MCP-oracle (taxonomy = record identity; infeasible in practice, used as a reference).
* **Endpoints (descriptive):** N1, the median SCP gap on truly new rows versus σ. N2, the median
  gap of MCP-exact, DCP and MCP-oracle versus σ. N3, the share of injected copies detected as
  "seen" by the exact key, versus σ.

## 5. Reporting

All prospective datasets are reported. Failed downloads, failed fits and infeasible splits are
logged and reported. No seed or dataset is selected by outcome.

## Amendment 1 (2026-10-21 ~21:05 UTC, before any prospective dataset was downloaded or run)

**Reason.** Since 20:50 UTC every connection from this environment to openml.org (www, api and
test hosts) is closed by the network proxy (`ws_closed_mid_exchange`). The UCI repository and
PyPI remain reachable.

**Contingency rule.**
* If OpenML is still unreachable at 22:50 UTC (two hours after the first failure), the
  prospective pool of §1 is replaced by **every dataset listed by the UCI Machine Learning
  Repository API** (`ucimlrepo.list_available_datasets()`; the snapshot is saved with the
  selection file). They are loaded with `fetch_ucirepo(id)`. If OpenML becomes reachable before
  then, §1 applies unchanged.
* UCI-specific eligibility, applied in this order and recorded: (i) exactly one target column
  that is non-missing; (ii) task taken from the UCI metadata (`Classification` → classification;
  else `Regression` → regression; otherwise excluded); (iii) 300 ≤ rows ≤ 5,000,000 and ≤ 2,000
  features.
* **Overlap with v1 (content-based, conservative).** Names differ between UCI and OpenML (e.g.
  "Breast Cancer Wisconsin (Original)" is OpenML *breast-w*), so a UCI dataset is excluded if its
  number of rows lies within ±2% of a v1 dataset whose number of features differs by at most 1,
  or if its normalized name matches a v1 name. This may exclude some unrelated datasets, which
  is acceptable.
* Everything else (subsampling rule, inclusion π̄ ≥ 0.01, learners, seeds, methods, tests P1–P5)
  is unchanged.

## Deviation note on Amendment 1 (2026-10-29)

The session was suspended between 2026-10-21 ~21:15 UTC and 2026-10-29, so the 22:50 UTC check
was never performed. When the prospective stage was finally run (2026-10-29 13:08 UTC), OpenML
was reachable again, and **no dataset had been downloaded from either source**. The primary pool
(§1, OpenML) was therefore used unchanged, and the UCI contingency was not triggered. The UCI
script (`code/experiments/prospective_selection_uci.py`) is kept but was not run.

## Deviation 2: selection details (2026-10-29, before any prospective outcome was computed)

1. **Parsing bug fixed.** The first selection attempt crashed because some OpenML "qualities" are
   lists, not numbers. The parser now skips non-numeric qualities (they are not used). No dataset
   was evaluated before the fix.
2. **Same data under two ids.** The selection (24 of 163 included) contained four data sets twice:
   wine_quality (287, 44136), yprop_4_1 (416, 45032), Mercedes_Benz_Greener_Manufacturing (42570,
   44061) and nyc-taxi-green-dec-2016 (44065, 44143); the Grinsztajn suites re-host AMLB data. §1
   de-duplicated only against v1. To avoid counting a data set twice, one copy per normalized name
   is kept, the one with the lowest id. The rule uses names only (no labels, no outcomes). This
   leaves **20** data sets.
3. **Transient download failures.** Seven downloads failed. Two are genuine parse failures (sparse
   ARFF, QSAR-TID-11 and QSAR-TID-10980) and stay excluded. Five were server-side (HTTP 503,
   "not found" while the API returned 503, or checksum errors, which were probably caused by two
   parallel download helpers writing the same file). These five were retried: Satellite (40900)
   succeeded at once. The others are retried every 2 minutes for at most 60 minutes, a cut-off set
   before retrying. Any data set that is still unavailable at the cut-off stays excluded as
   "download failed", as §1 prescribes. Data sets added by a successful retry go through the same
   label-free inclusion rule.
4. **Early start.** To save time, the prospective runs for the 20 data sets fixed by points 1–2
   were started while the retries were pending. The code and configuration are identical to
   `run_all.py --stage prospective`.
5. **Outcome of the retries (cut-off reached 15:20 UTC).** Satellite (40900) and volkert (41166)
   were downloaded; both have predicted exposure below 0.01 and are excluded by the inclusion
   rule. albert (41147) still returned HTTP 503 at the cut-off. Yolanda (42705) and Higgs (42769)
   failed OpenML's own md5 check on every attempt. A last attempt with the local download cache
   cleared fetched both files afresh and they still failed, so the mismatch is on the server side.
   These three stay excluded as "download failed". A selection re-run with the de-duplication
   rule (`results/logs/prospective_selection_rerun1.log`) reproduced the same **20** data sets.
