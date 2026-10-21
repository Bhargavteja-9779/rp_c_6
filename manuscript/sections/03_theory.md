# Problem formulation and theory

## Setting

Let $D=\{(x_i,y_i)\}_{i=1}^{N}$ be a data set whose rows are randomly partitioned, uniformly over all partitions of the given sizes, into a training set $T$ of $n_T$ rows, a calibration set $C$ of $n_C$ rows and a test set $E$. A *record group* is a maximal set of rows with identical feature vector; $m_g$ denotes the size of group $g$. Labels inside a group may differ. We call a calibration or test row *seen* if some training row has the same feature vector, and *novel* otherwise:
$$\kappa_T(x)=\mathrm{S}\ \text{if}\ \exists\, j\in T:\ x_j=x,\qquad \kappa_T(x)=\mathrm{N}\ \text{otherwise}.$$
The taxonomy $\kappa_T$ depends only on the training features. A model fitted on $T$ defines a nonconformity score $s(x,y)$. Split CP returns $\mathcal{C}(x)=\{y:\ s(x,y)\le\hat q\}$, where $\hat q$ is the $\lceil (n_C+1)(1-\alpha)\rceil$-th smallest calibration score ($+\infty$ if this rank exceeds $n_C$). Conditional on $T$, let $\pi$ be the probability that a randomly drawn test row is seen, $c$ the coverage of a random test row, and $c_{\mathrm S}=1-m_{\mathrm S}$ and $c_{\mathrm N}=1-m_{\mathrm N}$ the coverages of seen and novel test rows ($m$ denoting miscoverage).

**Lemma 0.** Conditional on the set of training rows, the remaining rows are assigned to $C$ and $E$ uniformly at random. Hence for any test row $j$ the rows of $C\cup\{j\}$ are exchangeable, and $\kappa_T$ is a fixed function.

Lemma 0 yields the familiar guarantee $c\ge 1-\alpha$, and $c\le 1-\alpha+\delta$ with $\delta=1/(n_C+1)$ when scores are almost surely distinct (Lei et al. 2018). Exact duplicates in $C$ produce tied scores. Ties preserve the lower bound but can break the upper one.

## How much coverage do novel records receive?

**Proposition 1.** For any model and score, conditional on $T$ with $\pi<1$,
$$c_{\mathrm N}=\frac{c-\pi c_{\mathrm S}}{1-\pi},\qquad \frac{\alpha-\delta-\pi m_{\mathrm S}}{1-\pi}\ \le\ m_{\mathrm N}\ \le\ \frac{\alpha-\pi m_{\mathrm S}}{1-\pi},$$
where the left inequality requires almost surely distinct scores.

*Proof.* By total probability, $c=\pi c_{\mathrm S}+(1-\pi)c_{\mathrm N}$, so $m_{\mathrm N}=(1-c-\pi m_{\mathrm S})/(1-\pi)$; insert $\alpha-\delta\le 1-c\le\alpha$. $\square$

Three consequences follow. First, novel records are under-covered exactly when seen records are over-covered ($m_{\mathrm S}<\alpha$), up to $\delta$. Second, in the *memorization limit* $m_{\mathrm S}\to 0$, reached when the model reproduces its training records, the novel miscoverage is $\alpha/(1-\pi)$: at $\alpha=0.1$ and $\pi=0.5$ one in five new records is missed while the reported coverage is 90%. Third, the gap $c_{\mathrm N}-(1-\alpha)\approx-\pi(\alpha-m_{\mathrm S})/(1-\pi)$ grows with the exposure $\pi$ and with the model's tendency to fit its training records. Both are testable dose–response predictions.

## Exposure can be predicted before any model is trained

**Proposition 2.** Let row $j$ belong to a group of size $m_g$. Then
$$\Pr\{\kappa_T(x_j)=\mathrm S\mid j\in E\}=1-\binom{N-m_g}{n_T}\Big/\binom{N-1}{n_T}\approx 1-(1-f)^{m_g-1},\quad f=\frac{n_T}{N-1},$$
and the expected exposure of a random test row is $\bar\pi=\sum_g (m_g/N)\,[1-\binom{N-m_g}{n_T}/\binom{N-1}{n_T}]$.

*Proof.* Given $j\in E$, the training set is a uniformly random $n_T$-subset of the other $N-1$ rows, and $x_j$ is novel exactly when none of the $m_g-1$ other copies is selected. $\square$

Combined with Proposition 1, a label-free audit of group sizes therefore yields a worst-case prediction $1-\alpha/(1-\bar\pi)$ for novel-record coverage. Li (2026) gives the analogous exposure probability for $K$-fold cross-validation.

## A remedy with a guarantee for any deployment mix

*Novelty-Mondrian CP* calibrates seen and novel rows separately. Let $C_k=\{i\in C:\kappa_T(x_i)=k\}$, $n_k=|C_k|$, and let $\hat q_k$ be the $\lceil (n_k+1)(1-\alpha)\rceil$-th smallest score in $C_k$ ($+\infty$ if that rank exceeds $n_k$). The prediction set is $\mathcal C^{\mathrm M}(x)=\{y: s(x,y)\le \hat q_{\kappa_T(x)}\}$.

**Proposition 3.** For $k\in\{\mathrm S,\mathrm N\}$, $\Pr\{Y\in\mathcal C^{\mathrm M}(X)\mid\kappa_T(X)=k,\,T\}\ge 1-\alpha$. With almost surely distinct scores the coverage is at most $1-\alpha+1/(n_k+1)$, conditional on $n_k$.

*Proof.* By Lemma 0, given $T$ the taxonomy is fixed and $C\cup\{j\}$ is exchangeable. Conditional on $\kappa_T(x_j)=k$ and on the multiset of category-$k$ rows in $C\cup\{j\}$, each of these $n_k+1$ rows is equally likely to be the test row. The usual quantile argument for Mondrian CP (Vovk et al. 2022) then applies within category $k$. $\square$

**Corollary 1.** For a deployment population that mixes seen and novel rows in any proportion $w\in[0,1]$, novelty-Mondrian CP has coverage at least $1-\alpha$. Under the same mix, split CP has coverage $w\,c_{\mathrm S}+(1-w)\,c_{\mathrm N}$, which for an all-new deployment ($w=0$) equals $c_{\mathrm N}$.

The remedy has an honest price. If fewer than $1/\alpha-1$ novel calibration rows are available, $\hat q_{\mathrm N}=+\infty$ and novel records receive the trivial set, signalling that the calibration data contain too little evidence about new records. An alternative is to split by record group, so that every test row is novel. Because groups have unequal sizes, that protocol has no row-level exchangeability guarantee, and we assess it empirically.

The analysis conditions on the finite data set. Its estimand is coverage of held-out rows, overall or restricted to rows that are novel with respect to the training set. Whether genuinely new deployment records behave like novel held-out rows is an assumption about the data-generating process, not a consequence of the theory.
