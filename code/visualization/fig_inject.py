"""Figure: copying rows on purpose creates the shortfall, in proportion to the share copied, for flexible
learners; separate calibration stays on target. Median over the 37 duplicate-free data sets; bands are 95%
bootstrap intervals of the median (resampling data sets)."""
import glob, os
import numpy as np
import pandas as pd
from style import COL, INK, RES, TWO, boot_ci, plt, save

LEARN = [("rf", "Random forest"), ("lgbm", "LightGBM"), ("logreg", "Logistic / ridge")]


def main():
    d = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RES, "inject", "inject_*.csv"))])
    if "error" in d:
        d = d[d.error.isna()]
    g = d.groupby(["task", "data_id", "model", "rate", "method"]).cov_novel.mean().reset_index()
    g["gap"] = 100 * (g.cov_novel - 0.9)
    fig, axs = plt.subplots(1, 3, figsize=(TWO, 54 / 25.4), sharey=True)
    for ax, (m, lab) in zip(axs, LEARN):
        for task, ls in (("classification", "-"), ("regression", "--")):
            for meth, key in (("SCP", "standard"), ("MCP", "fix")):
                q = g[(g.model == m) & (g.task == task) & (g.method == meth)]
                rates = sorted(q.rate.unique())
                med = [q[q.rate == r].gap.median() for r in rates]
                ci = np.array([boot_ci(q[q.rate == r].gap.values, np.median) for r in rates])
                ax.fill_between(rates, ci[:, 0], ci[:, 1], color=COL[key], alpha=0.15, lw=0)
                ax.plot(rates, med, ls=ls, marker="o", ms=2.5, color=COL[key])
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_title(lab)
        ax.set_xlabel("Share of rows copied")
        ax.set_xticks([0, 0.25, 0.5, 1.0])
        ax.grid(True)
    axs[0].set_ylabel("Coverage gap on new cases (pp)")
    h = [plt.Line2D([], [], color=COL["standard"]), plt.Line2D([], [], color=COL["fix"]),
         plt.Line2D([], [], color=INK, ls="-"), plt.Line2D([], [], color=INK, ls="--")]
    fig.legend(h, ["Standard calibration", "Seen/new calibrated separately", "Classification", "Regression"],
               loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.1))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_inject")


if __name__ == "__main__":
    main()
