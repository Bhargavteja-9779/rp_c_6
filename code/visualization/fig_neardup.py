"""Figure: copies with a little noise defeat the exact-match check, and the shortfall persists; calibration
by distance to the training rows stays on target. Random forest, half of the rows copied, median over 37 data
sets with 95% bootstrap intervals of the median."""
import glob, os
import numpy as np
import pandas as pd
from style import COL, INK, LAB, RES, TWO, boot_ci, plt, save

M = [("SCP", "standard"), ("MCP_exact", "fix"), ("DCP", "distance"), ("MCP_oracle", "reference")]


def main():
    N = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RES, "reinforcement", "neardup", "neardup_*.csv"))])
    g = N[N.model == "rf"].groupby(["task", "data_id", "sigma", "method"]).cov_truly_new.mean().reset_index()
    g["gap"] = 100 * (g.cov_truly_new - 0.9)
    fig, axs = plt.subplots(1, 2, figsize=(TWO, 56 / 25.4), sharey=True)
    sig = sorted(g.sigma.unique())
    for ax, task in zip(axs, ["classification", "regression"]):
        for j, (m, key) in enumerate(M):
            q = g[(g.task == task) & (g.method == m)]
            med = [q[q.sigma == s].gap.median() for s in sig]
            ci = np.array([boot_ci(q[q.sigma == s].gap.values, np.median) for s in sig])
            x = np.arange(len(sig)) + (j - 1.5) * 0.06
            ax.errorbar(x, med, yerr=[np.array(med) - ci[:, 0], ci[:, 1] - np.array(med)], marker="o", ms=3,
                        color=COL[key], elinewidth=0.8, capsize=0, ls="--" if key == "reference" else "-",
                        label=LAB[key] if key != "fix" else "Seen/new by exact match")
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_xticks(range(len(sig)), ["0 (exact)", "0.001", "0.01", "0.1"])
        ax.set_xlabel("Noise added to the copies (x feature SD)")
        ax.set_title(f"({'a' if task == 'classification' else 'b'}) {task.capitalize()}")
        ax.grid(True)
    axs[0].set_ylabel("Coverage gap on truly new cases (pp)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.09), fontsize=6.5)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_neardup")


if __name__ == "__main__":
    main()
