"""Publication figures, drawn only from aggregated result tables.

Journal spec (JKSU-CIS / Springer): Arial 8-12 pt, widths 84 mm (single) or 174 mm (double),
EPS for vector art plus high-resolution TIFF; a PNG copy is kept for the manuscript build.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .analysis import ALPHA0, C, GRID, INK, INK2, LEARNER_LABEL, LEARNERS  # noqa: E402

MM = 1 / 25.4
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "grid.color": GRID, "grid.linewidth": 0.5, "lines.linewidth": 1.5, "savefig.dpi": 600,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
SCP_C, MCP_C, LIM_C = C[0], C[1], INK2


def _save(fig, figs, name):
    for ext in ("png", "eps", "tiff"):
        kw = {"pil_kwargs": {"compression": "tiff_lzw"}} if ext == "tiff" else {}
        fig.savefig(os.path.join(figs, f"{name}.{ext}"), bbox_inches="tight", dpi=600 if ext != "png" else 300, **kw)
    plt.close(fig)


def _nominal(ax, a=ALPHA0):
    ax.axhline(1 - a, color=INK, lw=0.8, ls="-", zorder=1)


def fig_theory_and_exposure(aud, figs):
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 62 * MM))
    ax = axs[0]
    pi = np.linspace(0, 0.8, 200)
    for i, a in enumerate([0.05, 0.1, 0.2]):
        ax.plot(pi, 1 - a / (1 - pi), color=C[i], label=f"α = {a:g}")
        ax.axhline(1 - a, color=C[i], lw=0.6, ls=":")
    ax.set_xlabel("Exposure π (share of test rows with a training copy)")
    ax.set_ylabel("Coverage on novel records")
    ax.set_title("(a) Memorization limit 1 − α/(1 − π) (analytic)", loc="left")
    ax.set_ylim(0, 1.0)
    ax.grid(True)
    ax.legend(frameon=False, loc="lower left")
    ax = axs[1]
    a = aud.dropna(subset=["obs_exposure"])
    for i, (task, lab) in enumerate([("classification", "Classification (CC18)"), ("regression", "Regression (CTR23)")]):
        q = a[a.task == task]
        ax.scatter(q.pred_exposure, q.obs_exposure, s=14, color=C[i], edgecolor="white", linewidth=0.5,
                   label=lab, zorder=3)
    m = max(0.05, a.obs_exposure.max() * 1.05)
    ax.plot([0, m], [0, m], color=INK2, lw=0.8, ls="--", zorder=2)
    ax.set_xlabel("Predicted exposure (Prop. 2, label-free audit)")
    ax.set_ylabel("Observed exposure (mean over 10 splits)")
    ax.set_title("(b) Audit predicts exposure", loc="left")
    ax.grid(True)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    _save(fig, figs, "Fig1")


def fig_coverage_vs_exposure(agg, figs):
    fig, axs = plt.subplots(2, 5, figsize=(174 * MM, 80 * MM), sharex=True, sharey=True)
    pi = np.linspace(0, 0.85, 100)
    for r, (task, score) in enumerate([("classification", "lac"), ("regression", "absres")]):
        for c, m in enumerate(LEARNERS):
            ax = axs[r, c]
            q = agg[(agg.task == task) & (agg.model == m) & (agg.score == score) & (agg.protocol == "R")
                    & np.isclose(agg.alpha, ALPHA0) & (agg.set == "DUP")]
            s, mm = q[q.method == "SCP"], q[q.method == "MCP"]
            ax.plot(pi, 1 - ALPHA0 / (1 - pi), color=LIM_C, lw=0.8, ls="--", zorder=1)
            _nominal(ax)
            ax.scatter(s.exposure, s.cov_novel, s=10, color=SCP_C, edgecolor="white", linewidth=0.4, zorder=3,
                       label="Split CP")
            ax.scatter(mm.exposure, mm.cov_novel, s=10, color=MCP_C, edgecolor="white", linewidth=0.4, zorder=4,
                       marker="D", label="Novelty-Mondrian CP")
            ax.set_ylim(0.5, 1.01)
            ax.grid(True)
            if r == 0:
                ax.set_title(LEARNER_LABEL[m])
            if c == 0:
                ax.set_ylabel(("Classification (LAC)" if r == 0 else "Regression (|residual|)") + "\nnovel-record coverage")
            if r == 1:
                ax.set_xlabel("Exposure π")
    h, l = axs[0, 0].get_legend_handles_labels()
    h.append(plt.Line2D([], [], color=LIM_C, ls="--", lw=0.8))
    l.append("Memorization limit 1 − α/(1 − π)")
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, figs, "Fig2")


def fig_gap_by_learner(agg, figs):
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 62 * MM), sharey=True)
    for ax, (task, score, lab) in zip(axs, [("classification", "lac", "(a) Classification, LAC score"),
                                           ("regression", "absres", "(b) Regression, |residual| score")]):
        for i, m in enumerate(LEARNERS):
            for j, (meth, col) in enumerate([("SCP", SCP_C), ("MCP", MCP_C)]):
                q = agg[(agg.task == task) & (agg.model == m) & (agg.score == score) & (agg.protocol == "R")
                        & np.isclose(agg.alpha, ALPHA0) & (agg.set == "DUP") & (agg.method == meth)]
                g = (q.cov_novel - (1 - ALPHA0)).dropna().to_numpy()
                x = i + (j - 0.5) * 0.36
                jit = (np.random.default_rng(i * 10 + j).random(len(g)) - 0.5) * 0.18
                ax.scatter(x + jit, g, s=6, color=col, alpha=0.55, linewidth=0, zorder=2)
                if len(g):
                    ax.hlines(np.median(g), x - 0.15, x + 0.15, color=INK, lw=1.4, zorder=3)
        ax.axhline(0, color=INK, lw=0.8)
        ax.set_xticks(range(len(LEARNERS)))
        ax.set_xticklabels([LEARNER_LABEL[m] for m in LEARNERS], rotation=20)
        ax.set_title(lab, loc="left")
        ax.grid(True, axis="y")
    axs[0].set_ylabel("Novel-record coverage − (1 − α)")
    h = [plt.Line2D([], [], marker="o", ls="", color=SCP_C, ms=4), plt.Line2D([], [], marker="o", ls="", color=MCP_C, ms=4),
         plt.Line2D([], [], color=INK, lw=1.4)]
    fig.legend(h, ["Split CP", "Novelty-Mondrian CP", "Median over datasets"], loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, -0.05))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save(fig, figs, "Fig3")


def fig_dose(df, xvar, xlabel, figs, name, xticks=None, xticklabels=None):
    if not len(df):
        return
    s = df.groupby(["task", "data_id", "model", xvar, "method"])[["cov_novel", "exposure"]].mean().reset_index()
    s["gap"] = s.cov_novel - (1 - ALPHA0)
    tasks = [t for t in ("classification", "regression") if t in s.task.unique()]
    models = [m for m in ["logreg", "rf", "lgbm", "knn"] if m in s.model.unique()]
    fig, axs = plt.subplots(1, len(tasks), figsize=(174 * MM, 62 * MM), sharey=True, squeeze=False)
    for ax, task in zip(axs[0], tasks):
        for i, m in enumerate(models):
            q = s[(s.task == task) & (s.model == m)]
            for meth, ls, mk in [("SCP", "-", "o"), ("MCP", ":", "D")]:
                g = q[q.method == meth].groupby(xvar)["gap"].median()
                ax.plot(g.index, g.values, ls=ls, marker=mk, ms=3.5, color=C[i],
                        label=f"{LEARNER_LABEL[m]}" if meth == "SCP" else None)
        ax.axhline(0, color=INK, lw=0.8)
        ax.set_title(f"{'(a)' if task == tasks[0] else '(b)'} {task.capitalize()}", loc="left")
        ax.set_xlabel(xlabel)
        if xticks is not None:
            ax.set_xticks(xticks)
            if xticklabels is not None:
                ax.set_xticklabels(xticklabels)
        ax.grid(True)
    axs[0][0].set_ylabel("Median novel-record coverage − (1 − α)")
    h, l = axs[0][0].get_legend_handles_labels()
    h += [plt.Line2D([], [], color=INK2, ls="-"), plt.Line2D([], [], color=INK2, ls=":")]
    l += ["Split CP (solid)", "Novelty-Mondrian CP (dotted)"]
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.09))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    _save(fig, figs, name)


def fig_calibration(calib, aud, figs):
    if not len(calib):
        return
    sets = aud.set_index(["task", "data_id"])["set"]
    cal = calib[calib.protocol == "R"].copy()
    cal["oc_novel"] = cal.conf_novel - cal.acc_novel
    cal["oc_seen"] = cal.conf_seen - cal.acc_seen
    cal["oc_all"] = cal.conf_all - cal.acc_all
    ca = cal.groupby(["data_id", "model"])[["oc_all", "oc_seen", "oc_novel"]].mean().reset_index()
    ca = ca[[sets.get(("classification", i)) == "DUP" for i in ca.data_id]]
    fig, ax = plt.subplots(figsize=(174 * MM, 58 * MM))
    for i, m in enumerate(LEARNERS):
        q = ca[ca.model == m]
        for j, (col, lab, c) in enumerate([("oc_seen", "Seen rows", C[2]), ("oc_all", "All rows", INK2),
                                           ("oc_novel", "Novel rows", C[1])]):
            x = i + (j - 1) * 0.25
            v = q[col].dropna().to_numpy()
            jit = (np.random.default_rng(i * 7 + j).random(len(v)) - 0.5) * 0.12
            ax.scatter(x + jit, v, s=6, color=c, alpha=0.55, linewidth=0, label=lab if i == 0 else None)
            if len(v):
                ax.hlines(np.median(v), x - 0.1, x + 0.1, color=INK, lw=1.4)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(range(len(LEARNERS)))
    ax.set_xticklabels([LEARNER_LABEL[m] for m in LEARNERS])
    ax.set_ylabel("Overconfidence\n(mean confidence − accuracy)")
    ax.grid(True, axis="y")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.tight_layout()
    _save(fig, figs, "Fig6")


def fig_distance(dist_agg, figs):
    if not len(dist_agg):
        return
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 60 * MM), sharey=True)
    labels = ["Q1\n(near)", "Q2", "Q3", "Q4", "Q5\n(far)", "Seen"]
    for ax, task, lab in zip(axs, ["classification", "regression"], ["(a) Classification, LAC", "(b) Regression, |residual|"]):
        for i, m in enumerate(LEARNERS):
            q = dist_agg[(dist_agg.task == task) & (dist_agg.model == m) & (dist_agg.method == "SCP")]
            g = q.groupby("bin")["cov"].median()
            ax.plot(g.index, g.values, marker="o", ms=3, color=C[i], label=LEARNER_LABEL[m])
        q = dist_agg[(dist_agg.task == task) & (dist_agg.method == "DCP")]
        g = q.groupby("bin")["cov"].median()
        ax.plot(g.index, g.values, marker="D", ms=3, color=INK, ls=":", label="Distance-Mondrian (all learners)")
        _nominal(ax)
        ax.set_xticks(range(6))
        ax.set_xticklabels(labels)
        ax.set_xlabel("Distance to nearest training record (quintile bin)")
        ax.set_title(lab, loc="left")
        ax.grid(True)
    axs[0].set_ylabel("Median coverage (split CP)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=6, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    _save(fig, figs, "Fig7")


def make_all(res, agg, aud, calib, dist_agg, inj, cap):
    figs = os.path.join(res, "figures")
    os.makedirs(figs, exist_ok=True)
    fig_theory_and_exposure(aud, figs)
    fig_coverage_vs_exposure(agg, figs)
    fig_gap_by_learner(agg, figs)
    fig_dose(inj, "rate", "Injected duplication rate ρ", figs, "Fig4", xticks=[0, 0.1, 0.25, 0.5, 1.0])
    if len(cap):
        fig_dose(cap, "level", "Capacity level (0 = most flexible: k = 1 / leaf = 1 / C = 100)", figs, "Fig5",
                 xticks=[0, 1, 2, 3])
    fig_calibration(calib, aud, figs)
    fig_distance(dist_agg, figs)
