# Results I: three applications

Table 1 summarizes the applications, using random forests (RF) and LightGBM, and Fig. 1 shows the random-forest results at a glance. The "Seen share" and "Predicted" columns need only the data. The other columns come from 10 random splits.

![**Fig. 1** Coverage of 90% prediction sets in the three applications (random forest, mean of 10 random splits). Bars: overall coverage as reported by the usual check; circles: coverage on new cases with standard calibration; diamonds: coverage on new cases after the fix (separate calibration). Vertical line: the promised 90%](Fig_cases.png)

**Software-defect prediction.** The two largest NASA sets, mc1 and pc2, consist mostly of repeated modules: with a random split, about {{cs_mc1_pi}} of the test modules in mc1 have an exact copy in the training data. The usual evaluation looks fine. The random forest's 90% sets were right for {{cs_mc1_reported}}% of test modules in mc1 and {{cs_pc2_reported}}% in pc2. On genuinely new modules they were right only {{cs_mc1_new}}% and {{cs_pc2_new}}% of the time. The check flags both sets before any model is trained: its predicted worst-case shortfalls are {{cs_mc1_pred}} and {{cs_pc2_pred}} percentage points (pp). The actual shortfalls are smaller than this worst case, as expected for a model that does not memorize perfectly, but they are of the same order. Separate calibration brings coverage of new modules back to {{cs_mc1_fixed}}% and {{cs_pc2_fixed}}%.

The new modules also show *why* the standard sets fail. On new mc1 modules the average set size was {{cs_mc1_size_std}}, so many sets were *empty*: the model was so confident about familiar-looking inputs that, for new ones, it offered no label at all. After the fix the average size is {{cs_mc1_size_fix}}. For a review team, an empty set is a silent failure. A set that contains both labels is an honest "we don't know", which can be routed to manual inspection.

The smaller defect sets show the other side. Where the check predicts a shortfall of 2 pp or less (pc1, pc3, pc4, jm1, mw1), the measured coverage on new modules stayed within about 2 pp of 90%. The fix changed little there, and the check correctly signalled that standard conformal prediction was adequate.

**Network-intrusion detection.** The KDD Cup'99 data repeat the same connection records thousands of times, and about {{cs_kdd_pi}} of test connections have a training copy. The standard 90% sets covered {{cs_kdd_reported}}% of all test connections but {{cs_kdd_new}}% of new ones. With separate calibration, new-connection coverage was {{cs_kdd_fixed}}%. Overall coverage above 90% is itself a warning sign here: thousands of identical calibration records produce tied scores, which makes the standard method conservative overall while it under-covers the new connections.

**Phishing detection.** In the PhishingWebsites data, websites are described by 30 coarse features, so different sites often share the same profile. About {{cs_phish_pi}} of test sites have a training copy. Overall coverage was {{cs_phish_reported}}%, coverage on new sites {{cs_phish_new}}%, and {{cs_phish_fixed}}% after the fix.

Across the {{cs_n_flag}} applications that the check flagged (predicted shortfall larger than 2 pp), the random forest's coverage on new cases ranged from {{cs_flag_new_range}}% before the fix and {{cs_flag_fixed_range}}% after it. The cost is modest: new cases get somewhat larger sets, while seen cases keep small ones.

**Table 1** Applications at a target of 90% coverage. Seen share: fraction of test rows with an exact training copy (from the check). Predicted: worst-case shortfall $g^*$ from Eq. (3), computed without training. Overall: coverage reported by the usual check. New (standard) and New (fixed): coverage on new cases without and with separate calibration. Set size: average set size for new cases, standard → fixed. Means over 10 random splits

| Application | Data set | Model | Seen share | Predicted (pp) | Overall (%) | New, standard (%) | New, fixed (%) | Set size |
|---|---|---|---|---|---|---|---|---|
{{case_table_rows}}
