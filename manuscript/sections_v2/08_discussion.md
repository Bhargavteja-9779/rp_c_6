# Discussion

## What a practitioner should do

The results suggest a short routine for anyone who reports conformal prediction on tabular data.

1. **Check before training.** Hash the feature vectors, compute the expected share of seen test rows $\bar\pi$ with Eq. (2) and the label-pure share $\pi_P$, and from it the predicted shortfall $g^*$ of Eq. (3). This takes seconds and needs no model. In our data, a predicted shortfall smaller than about 2 pp together with an exposure below 10% reliably meant that nothing needed to change.
2. **Fix if flagged.** If the predicted shortfall is larger, or exposure is high, calibrate seen and new cases separately. When fewer than a few hundred new calibration rows are available, add the safety margin of Section 3.4. In regression, a distance-scaled residual is a sensible additional step.
3. **Report both numbers.** Give coverage on new cases next to overall coverage, and say how many test rows were seen. A reader can then judge the evaluation without rerunning it.

The routine matters most where a model will meet records it has never seen: a new software module, a new network connection, a new website. In these settings the reported coverage is used to make decisions, such as how many modules to send to manual review or which alerts to escalate. An empty prediction set for a new defect-prone module, as we saw on mc1, is a silent failure that no overall coverage figure reveals.

## Should one simply remove duplicates?

A common first reaction is to delete repeated rows before analysis. That is not always right. If the same input really does recur in deployment, for example a frequent network connection pattern, then repeats are part of the population, and deleting them changes the question being answered. Deleting repeats with conflicting labels also throws away information about label noise. Where records arrive over time, a time-based split (Sheridan 2013) is another honest evaluation, but it answers a different question again. Separate calibration avoids the choice: it keeps the data as they are and gives a valid promise for seen and for new cases, so the user can weight the two according to what is expected in deployment.

## Limitations

*Exact matches only.* The check detects only rows with identical feature values. Near-copies, such as the same record with a rounding difference or a re-measured value, are invisible to it. In our perturbation experiment, the exact-match check found none of the perturbed copies, and the remaining shortfall then had to be handled by distance-based calibration (Section 7.2). In practice the hashing can be made coarser (for example, by rounding features), but choosing that resolution is a modelling decision.

*The predicted shortfall is a worst case with known failure modes.* Eq. (3) assumes a model that memorizes pure repeats perfectly and finds all other rows equally hard. Regularized models fall short by less than predicted, which is harmless. The opposite case, where repeated rows that disagree slightly on a regression target are still easy (solar_flare), can make the actual shortfall much larger than predicted. We therefore recommend looking at exposure as well as at $g^*$. On fresh data, the predicted gap worked as a limit and as a screen for which data sets need the fix, but it did not rank data sets by the size of their shortfall (Section 7.1). It should be read as a warning level, not as a forecast of the exact coverage.

*The typical benchmark is not affected.* Our planned test of a general shortfall across benchmark data sets with repeats was negative, and our attempt to show the role of model flexibility by varying it within a learner was inconclusive. The problem is real but concentrated. We present the check precisely because it tells the two situations apart.

*Seen rows are defined by the training data.* Coverage on held-out new rows equals coverage on genuinely new records only if future records come from the same population. If deployment brings a distribution shift, separate calibration does not help with that; weighted or shift-aware conformal methods are needed (Tibshirani et al. 2019; Barber et al. 2023).

*Group splits and small calibration sets.* With very few new calibration rows (around 30), separate calibration is valid on average but noisy from split to split. The safety margin addresses this at the price of larger sets, and if no valid threshold exists it returns the full set, which is the honest answer.

*How the study was done.* The study, including its code and much of its text, was produced with substantial help from an AI system under human direction (see Declarations). Every number in the paper is computed by released code from archived result files. The fresh validation analysis was fixed in a time-stamped commit before its data were collected, and deviations from that plan are recorded in the repository.
