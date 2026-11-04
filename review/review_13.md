# Review 13 (simulated): applied reviewer (software engineering / security practice)

**Label: simulated review.** This is a role-separated pass by the AI system, not an external review.

**Recommendation as written by the simulated reviewer:** major revision. The routine is useful, but
the paper's own lead example shows that it fails the actual task: finding defective modules.

| # | Objection | Severity | Action taken | Status |
|---|---|---|---|---|
| 13.1 | New *defective* mc1 modules are covered 0% of the time even with the fix. For defect triage, that is the case that matters. | Major | Reported prominently (Sect. 6.3). Added a class-wise option to the tool (`classwise=True`: one threshold per seen/new group *and* class), which covers them at the cost of larger sets. The Discussion recommends it for rare classes. | Addressed (tool feature + text) |
| 13.2 | Random splits of NASA data do not reflect deployment, where new releases arrive over time. | Major | The NASA MDP data on OpenML carry no time stamps, so a time-ordered evaluation is not possible on them. Stated as a limitation and as future work. | Stated |
| 13.3 | LightGBM on KDD Cup'99 gives sets of about 9 labels for new connections. Coverage alone hides useless sets. | Moderate | Set sizes are reported next to coverage in every table (Table 4). The text now notes the uninformative LightGBM sets on KDD. | Addressed (text) |
| 13.4 | Wave 2 is almost entirely classification (25 of 27). | Minor | Stated as a limitation; regression evidence comes from the benchmarks, wave 1 (12 regression sets) and the copy experiments. | Stated |
| 13.5 | Is the tool usable outside the authors' pipeline? | Moderate | Validated post hoc on 20 files downloaded afresh, with its own defaults: verdicts 20/20, coverage within 2 SE 20/20. | Addressed (evidence) |
