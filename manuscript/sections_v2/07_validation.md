# Results III: fresh data and near-copies

## A fair test on data we had not seen

{{validation_text}}

## When copies are not exact

Real duplicates are often not byte-identical: a value is rounded differently, or a record is re-measured. To see what this does, we appended copies of half of the rows to each of the {{nd_n}} duplicate-free data sets and added a little noise to the copies' numeric features, from none up to 10% of each feature's standard deviation. Because we created the copies ourselves, we know which test rows are *truly* new, meaning that no version of the same record is in the training data.

Even very small noise blinds the exact-match check: at every noise level above zero it recognized {{nd_detect_cla}}% of the copies (Fig. 4). The problem itself does not go away, though. With exact copies, the random forest's coverage gap on truly new cases was {{nd_cla_0p0_SCP}} pp in classification. With noise of 0.1%, 1% and 10% of a standard deviation, it was {{nd_cla_0p001_SCP}}, {{nd_cla_0p01_SCP}} and {{nd_cla_0p1_SCP}} pp (regression: {{nd_reg_0p0_SCP}}, {{nd_reg_0p001_SCP}}, {{nd_reg_0p01_SCP}} and {{nd_reg_0p1_SCP}} pp). Small amounts of noise leave most of the shortfall in place; only noise of 10% of a standard deviation removes most of it in regression. The exact-match fix cannot see these copies: once noise is added, its result is close to that of the standard method ({{nd_cla_0p001_MCP_exact}} pp at the smallest noise level in classification).

Calibrating by *distance* to the nearest training rows does handle this case. We split calibration and test rows into six groups by that distance (exact copies form one group) and calibrated each group separately. Coverage of truly new cases then stayed at the target at every noise level ({{nd_cla_0p0_DCP}}, {{nd_cla_0p001_DCP}}, {{nd_cla_0p01_DCP}} and {{nd_cla_0p1_DCP}} pp in classification; {{nd_reg_0p0_DCP}} to {{nd_reg_0p1_DCP}} pp in regression), as good as an idealized version that knows the true record identity ({{nd_cla_0p01_MCP_oracle}} pp at 1% noise). In practice, then, the exact check is the right first step because it is simple and explains *why* coverage fails, and distance-based calibration is the safer fix whenever near-copies are plausible.

![**Fig. 4** Copies with added noise (random forest, median over {{nd_n}} data sets; half of the rows copied). Coverage gap on truly new cases, in percentage points, for the standard method, the exact-match fix, the distance-based fix, and a reference that knows which records were copied](Fig_neardup.png)
