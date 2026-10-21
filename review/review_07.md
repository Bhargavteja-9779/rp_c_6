# Review 07 — Efficiency and practical value

This is a distinct adversarial pass carried out by the same AI system in a different reviewer role. It was **not** conducted by independent human reviewers.

## R7.1 [MODERATE]

**Concern.** Pre-registered Experiment G (computational cost) had not been run.

**Response / action.** Run: hashing ≤ 0.17 s, audit ≤ 8 ms, MCP thresholds ≈ 40 µs vs LightGBM fit 0.6–2.8 s on 30,000-row data.

**Files / experiments.** code/experiments/cost_benchmark.py; tables/T9_cost.csv

**Status.** Fixed

## R7.2 [MINOR]

**Concern.** The practical threshold π̄ ≥ 0.1 is post hoc.

**Response / action.** Labelled as derived from our data.

**Files / experiments.** 06_discussion.md

**Status.** Disclosed
