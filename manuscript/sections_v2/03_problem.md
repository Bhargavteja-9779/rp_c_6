# Why repeated rows distort the check

## Setting and notation

A data set $D$ of $N$ rows is split at random into a training part $T$, a calibration part $C$ and a test part $E$ (60/20/20 in all our experiments). Rows with exactly the same feature values form a *record group*. A calibration or test row is *seen* if some training row has the same feature values, and *new* otherwise. The model is fitted on $T$ and produces a nonconformity score $s(x,y)$; split conformal prediction returns the set $\{y: s(x,y)\le\hat q\}$, where $\hat q$ is the $\lceil (n_C+1)(1-\alpha)\rceil$-th smallest calibration score (Lei et al. 2018). Throughout, $\alpha=0.1$, so the promise is 90% coverage.

Given the training part, the remaining rows are still assigned to calibration and test at random. This is all split conformal prediction needs: averaged over test rows, coverage is at least $1-\alpha$ (Vovk et al. 2022). The guarantee is about a random test **row**, and a random test row may well be a copy of a training row.

## The shortfall on new cases

Write $\pi$ for the share of test rows that are seen, $c$ for the overall coverage, and $c_S$ and $c_N$ for the coverage of seen and new rows. Because a test row is either seen or new,
$$c = \pi\,c_S + (1-\pi)\,c_N, \qquad\text{so}\qquad c_N = \frac{c-\pi c_S}{1-\pi}. \tag{1}$$
Since the method keeps $c$ close to $1-\alpha$, new cases are under-covered exactly when seen cases are over-covered. In the extreme case where every seen row is covered ($c_S=1$), the error rate on new cases becomes $\alpha/(1-\pi)$ instead of $\alpha$: with half of the test rows seen, one new case in five is missed while the check still reports 90%.

## The check: two numbers that can be computed before training

Equation (1) needs $c_S$, which requires a trained model. Two quantities that need only the data tell us in advance how large the problem can become.

*Exposure.* If a test row belongs to a group of $m$ identical rows and $n_T$ of the other $N-1$ rows go to training, the chance that none of its $m-1$ copies lands in training is $\binom{N-m}{n_T}/\binom{N-1}{n_T}$. Averaging over rows gives the expected share of seen test rows,
$$\bar\pi=\sum_g \frac{m_g}{N}\Big[1-\binom{N-m_g}{n_T}\Big/\binom{N-1}{n_T}\Big]. \tag{2}$$

*Label purity.* Exposure alone can mislead. If repeated rows disagree on the label (in survey or wage data, identical profiles often have different outcomes), memorizing them does not help the model, and seen rows are not over-covered. Let $\pi_P$ be the share of test rows whose training copies all carry exactly the test row's label (or, in regression, its target value). These are the rows a flexible model can simply look up. If those rows receive the lowest possible score and all other rows share one score distribution, the calibration threshold settles where $\pi_P+(1-\pi_P)F(\hat q)=1-\alpha$, so coverage of new cases tends to
$$c_N \to 1-\frac{\alpha}{1-\pi_P}, \qquad \text{a shortfall of } g^*=-\frac{\alpha\,\pi_P}{1-\pi_P}. \tag{3}$$
We call $g^*$ the *predicted shortfall*. It is a worst case for models that memorize their training rows; less flexible models should fall short by less. It can fail when repeated rows disagree on the label but are still easy to predict, for example when their regression targets differ only slightly. We test both points below. A short derivation of Eqs. (1)–(3) and a simulation check are given in Appendix A.

## The fix: calibrate seen and new cases separately

The remedy is to compute two thresholds, one from seen calibration rows and one from new calibration rows, and to apply each to the matching test rows. This is Mondrian conformal prediction (Vovk et al. 2022) with the categories "seen" and "new". Because the categories are fixed once the training part is chosen, calibration and test rows within each category remain exchangeable, and the usual argument gives coverage of at least $1-\alpha$ **separately** for seen and for new cases (Appendix A). The promise therefore holds for any mix of the two, including a deployment where every case is new. If too few new calibration rows exist (fewer than $1/\alpha-1$), the method honestly returns the full set for new cases.

Two variants are useful in practice. The first adds a *safety margin*: with only a few dozen new calibration rows, coverage varies noticeably from one split to the next, and choosing a slightly higher rank gives coverage of at least $1-\alpha$ with probability $1-\delta$ over the calibration draw (Vovk 2012). The second, for regression, scales each residual by the average distance to the ten nearest training rows (Papadopoulos et al. 2011), which automatically gives tighter intervals to rows that sit on top of a training copy.
