"""Figure: in the three applications, the usual check reports about 90% coverage while new cases are covered
far less; separate calibration restores it. Random forest, LAC, alpha = 0.1, 10 random splits; error bars are
95% bootstrap intervals of the mean over splits."""
import os
import numpy as np
import pandas as pd
from style import COL, INK, INK2, LAB, ONE, RES, boot_ci, plt, save

CASES = {1067: "Software defects", 1063: "Software defects", 1068: "Software defects", 1050: "Software defects",
         1049: "Software defects", 1053: "Software defects", 1056: "Software defects", 1069: "Software defects",
         1065: "Software defects", 1071: "Software defects", 1113: "Network intrusion", 4534: "Phishing websites"}


def load():
    rows = []
    for did, app in CASES.items():
        for src in ("raw", "external"):
            f = os.path.join(RES, src, f"classification_{did}.csv")
            if os.path.exists(f):
                d = pd.read_csv(f)
                if "error" in d:
                    d = d[d.error.isna()]
                d = d[(d.protocol == "R") & np.isclose(d.alpha, 0.1) & (d.score == "lac") & (d.model == "rf")]
                d["application"] = app
                rows.append(d)
                break
    return pd.concat(rows)


def main():
    d = load()
    stats = []
    for (app, name), g in d.groupby(["application", "name"]):
        s, m = g[g.method == "SCP"], g[g.method == "MCP"]
        stats.append(dict(app=app, name=name, overall=s.cov_all.mean(), std=s.cov_novel.mean(), fix=m.cov_novel.mean(),
                          std_ci=boot_ci(s.cov_novel), fix_ci=boot_ci(m.cov_novel)))
    S = pd.DataFrame(stats)
    order = ["Software defects", "Phishing websites", "Network intrusion"]
    S["o"] = S.app.map({a: i for i, a in enumerate(order)})
    S = S.sort_values(["o", "std"], ascending=[True, True]).reset_index(drop=True)
    grp = S.app.ne(S.app.shift()).cumsum() - 1
    yy = (np.arange(len(S)) + 1.3 * grp).to_numpy()
    fig, ax = plt.subplots(figsize=(ONE, 88 / 25.4))
    ax.axvline(90, color=INK, lw=0.8, zorder=1)
    for i, r in S.iterrows():
        ax.plot([100 * r["std"], 100 * r.fix], [yy[i]] * 2, color="#c9c8c3", lw=0.8, zorder=1)
        ax.errorbar(100 * r["std"], yy[i], xerr=[[100 * (r["std"] - r.std_ci[0])], [100 * (r.std_ci[1] - r["std"])]],
                    fmt="o", ms=3.6, color=COL["standard"], mec="white", mew=0.5, elinewidth=0.8, capsize=0, zorder=3)
        ax.errorbar(100 * r.fix, yy[i], xerr=[[100 * (r.fix - r.fix_ci[0])], [100 * (r.fix_ci[1] - r.fix)]],
                    fmt="D", ms=3.4, color=COL["fix"], mec="white", mew=0.5, elinewidth=0.8, capsize=0, zorder=4)
        ax.plot(100 * r.overall, yy[i], marker="|", ms=7, mew=1.2, color=INK2, ls="", zorder=5)
    ax.set_yticks(yy, list(S["name"]))
    for app, g in S.groupby("app", sort=False):
        ax.text(0.0, yy[g.index.min()] - 0.85, app, transform=ax.get_yaxis_transform(), ha="left", fontsize=7,
                color=INK2, style="italic")
    ax.set_ylim(yy.max() + 0.8, -1.7)
    ax.set_xlabel("Coverage of 90% prediction sets (%)")
    ax.grid(axis="x")
    h = [plt.Line2D([], [], marker="|", ls="", color=INK2, ms=7, mew=1.2),
         plt.Line2D([], [], marker="o", ls="", color=COL["standard"], ms=4),
         plt.Line2D([], [], marker="D", ls="", color=COL["fix"], ms=4)]
    ax.legend(h, ["Overall (usual check)", "New cases, standard", "New cases, fixed"], loc="lower center",
              bbox_to_anchor=(0.42, 1.0), ncol=3, frameon=False, handletextpad=0.2, columnspacing=0.8, fontsize=6.5)
    save(fig, "fig_cases")


if __name__ == "__main__":
    main()
