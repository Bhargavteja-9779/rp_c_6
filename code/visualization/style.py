"""Shared figure style: Liberation Sans (metric-compatible with Arial) at 8 pt, journal widths
84 mm (one column) and 174 mm (two columns), one fixed colour per method, light grey axes."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "paper", "figures")
MM = 1 / 25.4
ONE, TWO = 84 * MM, 174 * MM
INK, INK2, GRID = "#1b1b1a", "#52514e", "#e4e3df"
# colour-blind-safe categorical palette (validated in v1 with the dataviz validator); fixed per method
COL = {"standard": "#2a78d6", "fix": "#eb6834", "margin": "#eda100", "distance": "#1baf7a",
       "dedup": "#6250d6", "group": "#e87ba4", "reference": "#52514e"}
LAB = {"standard": "Standard calibration", "fix": "Seen/new calibrated separately", "margin": "+ safety margin",
       "distance": "Calibration by distance", "dedup": "Remove repeats, then calibrate", "group": "Group split",
       "reference": "Reference (true record identity)"}
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Liberation Sans", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "grid.color": GRID, "grid.linewidth": 0.5, "lines.linewidth": 1.4, "pdf.fonttype": 42, "ps.fonttype": 42,
    "axes.titleweight": "normal", "axes.titlelocation": "left"})


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, f"{name}.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(OUT, f"{name}.png"), bbox_inches="tight", dpi=300)
    plt.close(fig)


def boot_ci(x, stat=np.mean, n=1000, seed=0):
    """Percentile bootstrap 95% CI of a statistic (1,000 resamples)."""
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    b = stat(rng.choice(x, size=(n, len(x)), replace=True), axis=1)
    return tuple(np.percentile(b, [2.5, 97.5]))
