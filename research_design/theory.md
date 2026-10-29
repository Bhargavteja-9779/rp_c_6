# Theoretical analysis (Agent 6)

All results below are proved in this file. They are elementary consequences of the exchangeability
argument behind split conformal prediction (CP). The contribution is that they make explicit, and
exactly quantify, a failure mode that standard CP reporting hides.

## Setting

* A finite data set $D=\{(x_i,y_i)\}_{i=1}^N$ is randomly partitioned, uniformly over all
  partitions of the given sizes, into a training set $T$ ($n_T$ rows), a calibration set $C$
  ($n_C$ rows) and a test set $E$.
* Rows may share a feature vector. A **record group** is a maximal set of rows with identical
  $x$; $m_g$ is the size of group $g$. Labels within a group may differ (*conflicting* group).
* The **novelty taxonomy** is $\kappa_T(x)=\mathrm{S}$ (*seen*) if some training row has feature
  vector $x$, and $\mathrm{N}$ (*novel*) otherwise. It depends only on the training **features**.
* A model is fitted on $T$, giving a score $s(x,y)$; split CP outputs
  $\mathcal C(x)=\{y: s(x,y)\le \hat q\}$, with $\hat q$ the
  $\lceil (n_C+1)(1-\alpha)\rceil$-th smallest calibration score.
* Conditional on $T$, write $\pi=\Pr(\kappa_T(X)=\mathrm S\mid T)$ for a uniformly drawn test row,
  $c=\Pr(Y\in\mathcal C(X)\mid T)$, $c_k=\Pr(Y\in\mathcal C(X)\mid\kappa_T(X)=k,T)$, and
  $m_k=1-c_k$ (miscoverage).

**Lemma 0 (exchangeability given $T$).** Conditional on the *set* of training rows, the rows of
$D\setminus T$ are assigned to $C$ and $E$ uniformly at random. So for any test row $j$, the
multiset $C\cup\{j\}$ is exchangeable, and $\kappa_T$ is a fixed function.
*Proof.* A uniform random partition, conditioned on one block, is uniform on the remaining
blocks. ∎

Lemma 0 gives the usual marginal guarantee, $c\ge 1-\alpha$, and, if scores are almost surely
distinct (e.g. randomized tie-breaking), $c\le 1-\alpha+\delta$ with $\delta=1/(n_C+1)$ (Lei et al.
2018). Exact duplicates in $C$ (same $x$ **and** $y$) create **tied scores**. Ties keep the lower
bound but can break the upper bound.

## Proposition 1 (novel-record miscoverage under marginal calibration)

For any model and score, conditional on $T$ with $\pi<1$,
$$
c_{\mathrm N}=\frac{c-\pi c_{\mathrm S}}{1-\pi},\qquad\text{hence}\qquad
\frac{\alpha-\delta-\pi m_{\mathrm S}}{1-\pi}\;\le\; m_{\mathrm N}\;\le\;\frac{\alpha-\pi m_{\mathrm S}}{1-\pi},
$$
where the left inequality requires almost surely distinct scores.

*Proof.* By total probability, $c=\pi c_{\mathrm S}+(1-\pi)c_{\mathrm N}$. Substitute
$c_{\mathrm S}=1-m_{\mathrm S}$ and use $1-\alpha\le c\le 1-\alpha+\delta$:
$m_{\mathrm N}=1-c_{\mathrm N}=\frac{(1-\pi)-(c-\pi+\pi m_{\mathrm S})}{1-\pi}=\frac{1-c-\pi m_{\mathrm S}}{1-\pi}$,
and $\alpha-\delta\le 1-c\le\alpha$. ∎

**Consequences.**
1. Novel records are under-covered ($m_{\mathrm N}>\alpha$) **iff** seen records are over-covered
   ($m_{\mathrm S}<\alpha$), up to $\delta$. Over-coverage of seen records is what a model that fits
   its training records produces.
2. **Memorization limit.** If seen records are always covered ($m_{\mathrm S}=0$), the novel
   miscoverage is $\alpha/(1-\pi)$ (up to $\delta$). The nominal error rate is inflated by the
   factor $1/(1-\pi)$. For example, $\alpha=0.1$ and $\pi=0.5$ give 20% errors on new records while
   the reported coverage is 90%.
3. The gap $c_{\mathrm N}-(1-\alpha)\approx -\pi(\alpha-m_{\mathrm S})/(1-\pi)$ grows with
   exposure $\pi$ and with the model's capacity to fit training records (smaller $m_{\mathrm S}$).
   This gives the testable dose–response hypotheses H1a and H1b.

## Proposition 2 (exposure computable from a label-free audit)

Let row $j$ belong to group $g$ of size $m_g$, and let $f=n_T/(N-1)$. Then
$$
\Pr(\kappa_T(x_j)=\mathrm S\mid j\in E)=1-\frac{\binom{N-m_g}{n_T}}{\binom{N-1}{n_T}}
\approx 1-(1-f)^{m_g-1},
$$
and the expected exposure of a random test row is
$\bar\pi=\sum_g \frac{m_g}{N}\Big[1-\binom{N-m_g}{n_T}\big/\binom{N-1}{n_T}\Big]$.

*Proof.* Given $j\in E$, the training set is a uniform $n_T$-subset of the other $N-1$ rows. The
row is novel iff none of the $m_g-1$ other copies is chosen. ∎

Together with Proposition 1, $\bar\pi$ gives a model-free **worst-case novel-coverage
prediction** $1-\alpha/(1-\bar\pi)$ that can be computed before any model is trained. (Li 2026
gives the analogous exposure probability for K-fold CV and accuracy.)

## Proposition 3 (validity of novelty-Mondrian CP)

Let $C_k=\{i\in C:\kappa_T(x_i)=k\}$ with $n_k=|C_k|$, and let $\hat q_k$ be the
$\lceil(n_k+1)(1-\alpha)\rceil$-th smallest score in $C_k$ ($+\infty$ if that index exceeds
$n_k$). Define $\mathcal C^{\mathrm M}(x)=\{y:s(x,y)\le\hat q_{\kappa_T(x)}\}$. Then for
$k\in\{\mathrm S,\mathrm N\}$,
$$
\Pr\big(Y\in\mathcal C^{\mathrm M}(X)\mid \kappa_T(X)=k,\,T\big)\ge 1-\alpha,
$$
and with almost surely distinct scores the coverage is at most $1-\alpha+1/(n_k+1)$, conditional
on $n_k$.

*Proof.* By Lemma 0, given $T$ the taxonomy is fixed and $C\cup\{j\}$ is exchangeable. Condition
on $\kappa_T(x_j)=k$ and on the multiset of category-$k$ rows in $C\cup\{j\}$. Each of these
$n_k+1$ rows is equally likely to be the test row, so the test score's rank among them is uniform.
The standard quantile argument (Vovk et al. 2022, Mondrian CP) applies within category $k$. ∎

**Corollary 1 (any deployment mix).** For any test population that mixes seen and novel test
rows with arbitrary weight $w\in[0,1]$, novelty-Mondrian coverage is $\ge 1-\alpha$, because it is a
convex combination of two quantities that are each $\ge 1-\alpha$. Under the same mixture, split
CP has coverage $w c_{\mathrm S}+(1-w)c_{\mathrm N}$. When all deployment records are new
($w=0$), this equals $c_{\mathrm N}$, which Proposition 1 shows can be far below $1-\alpha$.

**Remark (price).** If $n_{\mathrm N}<1/\alpha-1$, then $\hat q_{\mathrm N}=+\infty$ and novel
records get the trivial set. This is the honest answer: there is not enough novel calibration
evidence. We record how often it happens.

## What the theory does *not* establish

* It conditions on the finite data set. The estimand is coverage of a randomly chosen held-out
  *row* of $D$ (marginal), or of a held-out row that is *novel relative to the training set*.
  Whether new deployment records behave like novel held-out rows is an **assumption** (records
  come from the same population and are new entities), not a theorem.
* It says nothing about *near*-duplicates; that extension is studied empirically and is
  exploratory.
* For the group-aware split (whole record groups assigned to one partition) we give no
  row-level guarantee. Groups of unequal size make row-level exchangeability between calibration
  and test fail. Its validity is assessed empirically.

## Proposition 4 (purity-adjusted memorization limit), added in the reinforcement cycle

Let $\pi_P$ be the probability that a random test row has at least one training row with the same
feature vector **and** every such training row carries exactly the test row's label (or target
value). Call these rows *memorizable*. Assume:

* **(M)** the fitted model assigns memorizable rows the minimal score 0 (for LAC, p̂_y = 1; for
  |res|, ŷ = y);
* **(E)** all other rows (novel rows, and seen rows whose training copies disagree in label) have
  scores drawn from one common distribution F with no atom at 0.

Calibration rows are memorizable with the same probability π_P. As n_C → ∞, the conformal
threshold converges to the (1 − α)-quantile of the mixture π_P δ_0 + (1 − π_P)F. If π_P < 1 − α,
this is the point t with π_P + (1 − π_P)F(t) = 1 − α, so novel rows are covered with probability

$$F(t) = 1 - \frac{\alpha}{1-\pi_P},\qquad\text{gap } g^* = -\frac{\alpha\,\pi_P}{1-\pi_P}.$$

If π_P ≥ 1 − α the threshold is 0 and novel coverage → 0.

*Proof.* Mixture quantile and the law of large numbers for the empirical quantile. ∎

Unlike Proposition 1, this needs **no trained model**. π_P depends only on labels and group
structure. (M) is an idealization that flexible learners approach and regularized learners do
not, so g* is a **memorization-limit prediction**. (E) fails when label-conflicting duplicate
groups are nonetheless easy, for example near-identical regression targets. Both failure modes
are tested empirically. Unit test `test_purity_limit_simulation` confirms the limit numerically.
