"""Figure: target versus achieved coverage on new cases. (a) Benchmark data sets with repeats, random forest,
three target levels: the overall coverage of standard calibration matches the target, its new-case coverage
falls below it, and separate calibration matches it. Medians over data sets with 95% bootstrap intervals.
(b) The 47 fresh data sets of waves 1 and 2 at a 90% target: per-data-set new-case coverage (dots) and medians."""
import glob, os
import numpy as np
import pandas as pd
from style import COL, GRID, INK, INK2, RES, TWO, boot_ci, plt, save


def main():
    fig, (a, b) = plt.subplots(1, 2, figsize=(TWO, 66 / 25.4), gridspec_kw=dict(width_ratios=[1, 1.35]))
    d = pd.read_csv(os.path.join(RES, "tables", "per_dataset_results.csv"))
    d = d[(d.protocol == "R") & (d.set == "DUP") & d.score.isin(["lac", "absres"]) & (d.model == "rf")]
    a.plot([77, 97], [77, 97], color=INK2, ls=":", lw=0.8)
    for (col, meth, key, mk, lab) in (("cov_all", "SCP", "reference", "s", "Standard, all cases"),
                                     ("cov_novel", "SCP", "standard", "o", "Standard, new cases"),
                                     ("cov_novel", "MCP", "fix", "D", "Seen/new separately, new cases")):
        xs, ms, lo, hi = [], [], [], []
        for alpha in (0.2, 0.1, 0.05):
            v = 100 * d[(d.method == meth) & np.isclose(d.alpha, alpha)][col].values
            xs.append(100 * (1 - alpha)); ms.append(np.median(v)); c = boot_ci(v, np.median); lo.append(c[0]); hi.append(c[1])
        off = {"reference": -0.6, "standard": 0, "fix": 0.6}[key]
        a.errorbar(np.array(xs) + off, ms, yerr=[np.array(ms) - lo, np.array(hi) - ms], fmt=mk, ms=3.5, color=COL[key],
                   elinewidth=0.9, capsize=0, label=lab)
        # worst data set as a faint marker
    a.set_xlabel("Target coverage (%)")
    a.set_ylabel("Achieved coverage (%), median")
    a.set_xticks([80, 90, 95])
    a.set_title("(a) Benchmarks with repeats, random forest")
    a.grid(True)
    a.legend(frameon=False, loc="upper left", fontsize=6.3)
    # (b) fresh data
    files = glob.glob(os.path.join(RES, "reinforcement", "prospective", "prosp_*.csv")) + \
        glob.glob(os.path.join(RES, "reinforcement", "prospective_w2", "w2_*.csv"))
    P = pd.concat([pd.read_csv(f) for f in files])
    if "error" in P:
        P = P[P.error.isna()]
    P = P[(P.model == "rf") & P.score.isin(["lac", "absres"])]
    g = P.groupby(["data_id", "method"]).cov_novel.mean().reset_index()
    meths = [("SCP", "standard", "Standard"), ("MCP", "fix", "Seen/new\nseparately"), ("PAC_MCP", "margin", "+ safety\nmargin"),
             ("DCP", "distance", "By distance")]
    rng = np.random.default_rng(0)
    b.axhline(90, color=INK, lw=0.8)
    for i, (m, key, lab) in enumerate(meths):
        v = 100 * g[g.method == m].cov_novel.values
        b.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=7, color=COL[key], alpha=0.75, lw=0)
        c = boot_ci(v, np.median)
        b.errorbar(i + 0.32, np.median(v), yerr=[[np.median(v) - c[0]], [c[1] - np.median(v)]], fmt="_", ms=9,
                   color=INK, elinewidth=1.0, capsize=0)
    b.set_xticks(range(len(meths)), [lab for _, _, lab in meths])
    b.set_ylabel("New-case coverage (%), per data set")
    b.set_title(f"(b) {g.data_id.nunique()} fresh data sets, random forest, target 90%")
    b.grid(axis="y")
    fig.tight_layout()
    save(fig, "fig_validity")


if __name__ == "__main__":
    main()
