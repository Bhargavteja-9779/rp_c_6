"""Figure: the check's predicted worst-case gap against the observed gap on the 47 fresh data sets. Every data
set with a real shortfall (shaded, worse than -2 pp) was flagged. Observed gap: the worse of random forest and
LightGBM, mean over 20 splits, with a 95% bootstrap interval over splits."""
import glob, os
import numpy as np
import pandas as pd
from style import COL, GRID, INK, INK2, ONE, RES, boot_ci, plt, save


def main():
    R = os.path.join(RES, "reinforcement")
    sc = pd.read_csv(os.path.join(R, "tables", "screening.csv"))
    files = glob.glob(os.path.join(R, "prospective", "prosp_*.csv")) + glob.glob(os.path.join(R, "prospective_w2", "w2_*.csv"))
    P = pd.concat([pd.read_csv(f) for f in files])
    if "error" in P:
        P = P[P.error.isna()]
    P = P[(P.method == "SCP") & P.model.isin(["rf", "lgbm"]) & P.score.isin(["lac", "absres"])]
    P["gap"] = 100 * (P.cov_novel - 0.9)
    rows = []
    for _, r in sc.iterrows():
        q = P[P.data_id.astype(str) == str(r.data_id)]
        mm = q.groupby("model").gap.mean()
        worst = mm.idxmin()
        v = q[q.model == worst].gap.values
        lo, hi = boot_ci(v)
        rows.append(dict(name=r["name"], wave=r.wave, flag=r.flag, g=100 * r.g_star, obs=v.mean(), lo=lo, hi=hi))
    S = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(ONE, 80 / 25.4))
    lo_ = min(S.g.min(), S.lo.min()) - 4
    ax.axhspan(lo_, -2, color="#fbe3dc", lw=0, zorder=0)
    ax.plot([lo_, 2], [lo_, 2], color=INK2, ls="--", lw=0.8, zorder=1, label="Observed = predicted")
    ax.axhline(0, color=INK, lw=0.7, zorder=1)
    for wave, mk in ((1, "o"), (2, "D")):
        for flag in (True, False):
            q = S[(S.wave == wave) & (S.flag == flag)]
            ax.errorbar(q.g, q.obs, yerr=[q.obs - q.lo, q.hi - q.obs], fmt=mk, ms=3.3, elinewidth=0.6, capsize=0,
                        color=COL["fix"] if flag else COL["standard"], mfc=COL["fix"] if flag else "white", mew=0.8,
                        zorder=3, label=f"Wave {wave}, {'flagged' if flag else 'not flagged'}")
    for _, r in S[S.obs < -5].iterrows():
        nm = (r["name"].replace("analcatdata_", "").replace(" (Android Permissions)", "")
              .replace("Early Stage Diabetes Risk Prediction", "early diabetes").replace("Congressional Voting Records", "voting")
              .replace("Maternal Health Risk", "maternal health").replace("Skin Segmentation", "skin segmentation"))
        ax.annotate(nm, (r.g, r.obs), xytext=(4, -1), textcoords="offset points", fontsize=6, color=INK2)
    ax.set_xlim(lo_, 3)
    ax.set_ylim(lo_, 12)
    ax.set_xlabel("Predicted worst-case gap, no model (pp)")
    ax.set_ylabel("Observed gap on new cases (pp)")
    ax.grid(True, color=GRID)
    ax.legend(loc="lower right", fontsize=6, frameon=False)
    save(fig, "fig_screen")


if __name__ == "__main__":
    main()
