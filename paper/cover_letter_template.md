---
geometry: margin=2.3cm
fontsize: 11pt
---

[DATE]

The Editor-in-Chief
Journal of King Saud University -- Computer and Information Sciences

Dear Editor,

We submit the manuscript **"Duplicate Data Rows Make Prediction Uncertainty Look Better Than It Is: A Simple Check and Fix for New Cases"** for consideration as a regular research article.

**The practical problem.** Teams increasingly attach conformal prediction sets to classifiers and regressors to state how sure a prediction is. They check the promised coverage on a random test split. When tabular data contain repeated rows, as is common in software-defect, network-intrusion, phishing and clinical data, this check is misleading: many test rows have a copy in the training data. On the NASA mc1 defect data, the usual check reports {{cs_mc1_reported}}% coverage for 90% sets, while genuinely new modules are covered only {{cs_mc1_new}}% of the time and {{tool_std_empty}} of them receive an empty set.

**What the paper offers.**

* A check that needs only the data. It predicts, before any model is trained, how far coverage of new cases can fall. It includes a new closed-form expression for the share of test rows whose training copies carry the same label.
* A fix: calibrating seen and new cases separately. This is standard Mondrian calibration, applied to the groups that the data imply.
* A reporting rule.
* An open-source tool, *covercheck*, that runs all three steps and writes a one-page report.

**The evidence.**

* **Data and models.** The routine was tested on {{cs_n_flag_total}} application data sets, {{n_total}} benchmark data sets and controlled experiments with exact and noisy copies. It was also tested on two fresh collections of {{pr_n}} and {{w2_n}} data sets, each analysed under a plan committed before its data were downloaded. Learners were random forests, LightGBM and linear models.
* **The check.** It flagged all {{scp_pos}} fresh data sets with a real shortfall (95% CI for sensitivity {{scp_sens_ci}}).
* **The fix.** With it, new-case coverage never fell more than {{w2_worst_fix_abs}} percentage points below the target.
* **The tool.** It reproduced the research pipeline on {{tv_n}} data files downloaded afresh.
* **Reproducibility.** Every number in the paper is generated from archived result files.

**Fit with the journal.** The paper addresses a practical, broadly relevant problem in machine-learning evaluation. It is framed around real applications and delivers usable software, which matches the journal's applied computer-science readership.

**Main limitations, stated in the paper.**

* The predicted gap works as a limit and a screen, not as a forecast: on the first fresh collection it did not rank data sets by the size of their shortfall.
* Exact matching misses near-copies; calibration by distance handles them.
* A promise over all new cases does not protect a rare class.
* Several analyses were added after results were seen; they are labelled as such.
* The work was carried out with substantial assistance from an AI system, as declared in the manuscript. The authors take full responsibility for it.

**Statements.** [AUTHOR TO CONFIRM: This manuscript is original, has not been published, and is not under consideration elsewhere. All authors have approved the submission.] All data sets are public (OpenML and UCI identifiers are listed in the Supplementary Material). The method is available as the open-source package *covercheck*, and the full pipeline is in a version-controlled repository [AUTHOR TO COMPLETE: DOI or anonymized link].

Sincerely,

[CORRESPONDING AUTHOR NAME, AFFILIATION, E-MAIL]
