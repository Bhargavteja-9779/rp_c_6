# Review 03 — Experimental design and statistics

This is a distinct adversarial pass carried out by the same AI system in a different reviewer role. It was **not** conducted by independent human reviewers.

## R3.1 [MAJOR]

**Concern.** The confirmatory set DUP (π̄ ≥ 0.01) mixes datasets with negligible expected gaps with a few at-risk ones, so a median test of a heterogeneous effect was poorly targeted and underpowered.

**Response / action.** Acknowledged in the Discussion and Limitations. Exposure-stratified analysis added, labelled exploratory. Dataset-level seed CIs added for π̄ ≥ 0.3 (20 of 45 SCP combinations below zero vs 1 for MCP). The injection experiment provides confirmatory causal evidence.

**Files / experiments.** analysis.py (_seedlevel, X2, X3)

**Status.** Fixed / disclosed

## R3.2 [MODERATE]

**Concern.** Spearman p-values for H1a are not corrected for multiplicity.

**Response / action.** Stated in Methods.

**Files / experiments.** 04_methods.md

**Status.** Fixed

## R3.3 [MODERATE]

**Concern.** Bootstrap CIs of medians from 12 regression datasets are coarse.

**Response / action.** Reported as such. The conclusions do not rest on the regression medians alone.

**Files / experiments.** —

**Status.** Disclosed

## R3.4 [MODERATE]

**Concern.** MCP-R gap −5.8 pp on solar_flare appeared to contradict Proposition 3.

**Response / action.** Verification with 200 extra splits: 0.909 (95% CI 0.899–0.918). Reported in the Results and as a limitation (split-to-split variability with small novel calibration sets).

**Files / experiments.** code/experiments/verify_solar_flare.py

**Status.** Fixed
