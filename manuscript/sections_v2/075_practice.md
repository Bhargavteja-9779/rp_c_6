# Putting it into practice

## Which fix should one use?

Several remedies are possible, and the obvious one is to remove the repeated rows. We compared six options on the twelve application data sets, using the same random splits and random forests (Table 2). The data sets and splits are those of Section 5, and the comparison was specified before it was run.

**Table 2** Remedies on the twelve application data sets (random forest, 90% target, 10 random splits each). New-case coverage: median and worst data set. Seen cases: coverage and mean set size for test rows with a training copy. Training data used: median share of training rows kept

| Method | Data sets | New-case coverage, median (%) | New-case coverage, worst (%) | Empty sets for new cases (%) | Seen cases: coverage (%) / set size | Training data used |
|---|---|---|---|---|---|---|
{{rem_table_rows}}

Three points stand out. First, what matters is *which rows the calibration uses*. Every remedy that calibrates on new rows brings new-case coverage to the target, and standard calibration does not. Second, removing repeats works about as well for new cases ({{rem_Dedup_new_med}}% median), but it throws data away: on mc1 the model is trained on {{rem_mc1_train_dedup}} instead of {{rem_mc1_train_full}} modules. It also gives the seen cases the sets that were calibrated for new ones, so seen cases are over-covered ({{rem_Dedup_seen_cov}}%) with larger sets ({{rem_Dedup_seen_size}} versus {{rem_MCP_seen_size}} labels). Third, a group split gives honest coverage for new cases. It cannot, however, say anything about seen cases, and on KDD Cup'99 it was infeasible in {{rem_gscp_kdd_fail}} splits, because a single group of identical connections is larger than the test part. Separate calibration keeps all the data, works with any split and gives a valid promise for seen and new cases at once. The safety margin trades slightly larger sets for a better worst case ({{rem_PAC_MCP_new_min}}% against {{rem_MCP_new_min}}%) and no empty sets for new cases.

## A tool for practitioners

To make the routine easy to adopt, we packaged it as an open-source Python library and command-line tool, *covercheck*. It has three parts, one for each step.

* `check(X, y)` computes Eqs. (2), (2b) and (3) and returns a verdict with reasons. No model is needed.
* `SeenNewConformal` wraps any scikit-learn estimator and calibrates seen and new cases separately. It has options for the distance-based variant (`mode="distance"`) and for the safety margin (`delta=0.1`).
* `evaluate` reports coverage on all, seen and new cases over repeated random splits.

The command `covercheck data.csv --target label --html report.html` runs all three steps and writes a one-page report (Fig. 6). On the {{tool_rows}} mc1 modules, the check took {{tool_check_s}} s. It predicted a worst-case gap of {{tool_gap}} pp, because {{tool_pip}} of test modules will have a training copy with the same label. The report then shows the problem directly: overall coverage of {{tool_std_all}}%, but {{tool_std_new}}% for new modules, {{tool_std_empty}} of which receive an empty set. With the fix, new modules are covered {{tool_fix_new}}% of the time. The tool has its own test suite. It includes a simulation check of the closed-form formula (2b) and a check that the fix restores new-case coverage in classification and regression.

![**Fig. 6** The one-page report produced by *covercheck* for the NASA mc1 defect data: the check (no model needed), its verdict, and coverage on all, seen and new cases with and without the fix (random forest, 10 random splits)](Fig_tool.png)
