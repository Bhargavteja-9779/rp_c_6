"""Figure: on the twelve application data sets, every remedy that calibrates on new rows reaches the target
for new cases; separate calibration does so without discarding data and gives seen cases smaller sets than
removing repeats. Random forest, 10 splits; dots are data sets; bars are medians with 95% bootstrap intervals."""
import os
import numpy as np
import pandas as pd
from style import COL, INK, RES, TWO, boot_ci, plt, save

M = [("SCP", "standard", "Standard"), ("Dedup", "dedup", "Remove\nrepeats"), ("GSCP", "group", "Group\nsplit"),
     ("MCP", "fix", "Seen/new\nseparately"), ("PAC_MCP", "margin", "+ safety\nmargin"), ("DCP", "distance", "By\ndistance")]


def main():
    g = pd.read_csv(os.path.join(RES, "reinforcement", "tables", "remedies_summary.csv"))
    g = g[g.model == "rf"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(TWO, 58 / 25.4), gridspec_kw=dict(width_ratios=[1.25, 1]))
    rng = np.random.default_rng(1)
    a.axhline(90, color=INK, lw=0.8)
    for i, (m, key, lab) in enumerate(M):
        v = 100 * g[g.method == m].cov_new.values
        a.scatter(i + rng.uniform(-0.15, 0.15, len(v)), v, s=8, color=COL[key], alpha=0.8, lw=0)
        c = boot_ci(v, np.median)
        a.errorbar(i + 0.3, np.median(v), yerr=[[np.median(v) - c[0]], [c[1] - np.median(v)]], fmt="_", ms=8,
                   color=INK, elinewidth=1.0)
    a.set_xticks(range(len(M)), [lab for *_, lab in M])
    a.set_ylabel("New-case coverage (%)")
    a.set_title("(a) Coverage of new cases")
    a.grid(axis="y")
    MS = [x for x in M if x[0] != "GSCP"]
    for i, (m, key, lab) in enumerate(MS):
        v = g[g.method == m].size_seen.values
        b.scatter(i + rng.uniform(-0.15, 0.15, len(v)), v, s=8, color=COL[key], alpha=0.8, lw=0)
        c = boot_ci(v, np.median)
        b.errorbar(i + 0.3, np.median(v), yerr=[[np.median(v) - c[0]], [c[1] - np.median(v)]], fmt="_", ms=8,
                   color=INK, elinewidth=1.0)
    b.set_xticks(range(len(MS)), [lab for *_, lab in MS])
    b.set_ylabel("Mean set size, seen cases")
    b.set_title("(b) Set size for seen cases")
    b.grid(axis="y")
    fig.tight_layout()
    save(fig, "fig_remedies")


if __name__ == "__main__":
    main()
