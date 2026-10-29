"""Case-study table for the application framing: software-defect prediction (NASA MDP),
network-intrusion detection (KDD Cup'99) and phishing-website detection. Uses only existing
v1 result files (protocol R, LAC, alpha = 0.1) plus the label-level check quantities."""
import glob, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dupcp.audit import purity_bound

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
A = 0.1
CASES = {  # data_id: (application, source folder)
    1067: ("Software defects", "raw"), 1063: ("Software defects", "raw"), 1068: ("Software defects", "raw"),
    1050: ("Software defects", "raw"), 1049: ("Software defects", "raw"), 1053: ("Software defects", "raw"),
    1056: ("Software defects", "external"), 1069: ("Software defects", "external"),
    1065: ("Software defects", "external"), 1071: ("Software defects", "external"),
    1113: ("Network intrusion", "external"), 4534: ("Phishing websites", "raw"),
}
retro = pd.read_csv(os.path.join(ROOT, "results", "reinforcement", "purity_retrospective.csv"))
rows = []
for did, (app, src) in CASES.items():
    f = os.path.join(ROOT, "results", src, f"classification_{did}.csv")
    d = pd.read_csv(f)
    if "error" in d:
        d = d[d.error.isna()]
    d = d[(d.protocol == "R") & np.isclose(d.alpha, A) & (d.score == "lac")]
    aud = json.load(open(os.path.join(ROOT, "results", src, f"audit_classification_{did}.json")))
    pr = retro[(retro.data_id == did) & (retro.model == "rf")]
    for model in ["rf", "lgbm", "logreg"]:
        q = d[d.model == model]
        s, m = q[q.method == "SCP"], q[q.method == "MCP"]
        rows.append(dict(application=app, data_id=did, name=aud["name"], n_rows=aud["n_raw"], model=model,
                         dup_row_frac=aud["dup_row_frac"], pi=float(pr.pi.iloc[0]) if len(pr) else np.nan,
                         pi_p=float(pr.pi_p.iloc[0]) if len(pr) else np.nan,
                         reported_cov=s.cov_all.mean(), new_cov_standard=s.cov_novel.mean(),
                         new_cov_fixed=m.cov_novel.mean(), seen_cov_standard=s.cov_seen.mean(),
                         size_new_standard=s.size_novel.mean(), size_new_fixed=m.size_novel.mean()))
cs = pd.DataFrame(rows)
cs["predicted_gap"] = [purity_bound(p, A) if p == p else np.nan for p in cs.pi_p]
cs["observed_gap"] = cs.new_cov_standard - (1 - A)
os.makedirs(os.path.join(ROOT, "results", "reinforcement", "tables"), exist_ok=True)
cs.to_csv(os.path.join(ROOT, "results", "reinforcement", "tables", "case_studies.csv"), index=False)
pd.set_option("display.width", 250)
print(cs[cs.model == "rf"][["application", "name", "n_rows", "pi", "pi_p", "predicted_gap", "reported_cov",
                            "new_cov_standard", "new_cov_fixed", "size_new_standard", "size_new_fixed"]].round(3).to_string())

# Figure: dot plot of overall vs new-case coverage, random forest, all application data sets
from dupcp.figures import MM, _save, plt  # noqa: E402
from dupcp.analysis import C, INK, INK2  # noqa: E402
q = cs[cs.model == "rf"].sort_values(["application", "new_cov_standard"], ascending=[False, False]).reset_index(drop=True)
grp = q.application.ne(q.application.shift()).cumsum() - 1  # group index, one blank row between groups
yy = (np.arange(len(q)) + 1.2 * grp).to_numpy()
fig, ax = plt.subplots(figsize=(84 * MM, 82 * MM))
ax.axvline(100 * (1 - A), color=INK, lw=0.8, zorder=1)
ax.hlines(yy, 100 * q.new_cov_standard, 100 * q.new_cov_fixed, color=INK2, lw=0.6, zorder=2)
ax.scatter(100 * q.reported_cov, yy, s=22, marker="|", color=INK2, zorder=3, label="Overall (usual check)")
ax.scatter(100 * q.new_cov_standard, yy, s=18, color=C[0], edgecolor="white", linewidth=0.5, zorder=4,
           label="New cases, standard")
ax.scatter(100 * q.new_cov_fixed, yy, s=18, marker="D", color=C[1], edgecolor="white", linewidth=0.5, zorder=5,
           label="New cases, fixed")
ax.set_yticks(yy, list(q["name"]))
for app, g in q.groupby("application", sort=False):
    ax.text(0.0, yy[g.index.min()] - 0.75, app, transform=ax.get_yaxis_transform(), ha="left", va="bottom",
            fontsize=6.5, color=INK2, style="italic")
ax.set_ylim(yy.max() + 0.7, -1.6)
ax.set_xlabel("Coverage of 90% prediction sets (%)")
ax.grid(axis="x")
ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, frameon=False, handletextpad=0.2, columnspacing=0.8,
          fontsize=6.5)
FIG = os.path.join(ROOT, "results", "reinforcement", "figures")
os.makedirs(FIG, exist_ok=True)
_save(fig, FIG, "Fig_cases")
