"""Figure: the check-fix-report routine, drawn with real rows of the NASA mc1 data. The rows shown are chosen by
a fixed rule: the first three rows (in data-set order) of the largest group of identical modules, and the first
row that has no copy. All numbers are read from result files."""
import json, os, sys
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from style import COL, INK, INK2, RES, ROOT, TWO, plt, save

sys.path.insert(0, os.path.join(ROOT, "code", "src"))
from dupcp.data import load_dataset  # noqa: E402


BOXES = []


def box(ax, x, y, w, h, title, lines, color, title_col=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", lw=0.9,
                                ec=color, fc="white"))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.11), w, 0.11, boxstyle="round,pad=0.006,rounding_size=0.012",
                                lw=0, fc=color, alpha=0.18))
    texts = [ax.text(x + 0.01, y + h - 0.055, title, fontsize=7, weight="bold", color=title_col, va="center")]
    BOXES.append(((x, y, w, h), texts))
    for i, (t, kw) in enumerate(lines):
        texts.append(ax.text(x + 0.01, y + h - 0.16 - i * 0.087, t, fontsize=kw.get("size", 6.2), va="top",
                color=kw.get("color", INK), family=kw.get("family", "sans-serif"), weight=kw.get("weight", "normal")))


def arrow(ax, x0, x1, y):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=9, lw=1.0, color=INK2))


def main():
    d = load_dataset(1056, "classification", os.path.join(ROOT, "data_cache"))
    X, y, keys = d["X"], d["y"], d["keys"]
    s = pd.Series(keys)
    big = s.value_counts().index[0]
    grp = np.flatnonzero(keys == big)[:3]
    single = int(np.flatnonzero(s.map(s.value_counts()).values == 1)[0])
    rows = list(grp) + [single]
    cols = ["LOC_TOTAL", "CYCLOMATIC_COMPLEXITY", "NUM_OPERATORS"]
    tc = json.load(open(os.path.join(RES, "reinforcement", "tables", "tool_mc1_check.json")))
    tm = pd.read_csv(os.path.join(RES, "reinforcement", "tables", "tool_mc1.csv"), index_col=0)
    ex = json.load(open(os.path.join(RES, "e12_qualitative", "examples.json")))["thresholds"]
    gsize = int((keys == big).sum())

    fig, ax = plt.subplots(figsize=(TWO, 70 / 25.4))
    ax.set_xlim(-0.012, 1.012)
    ax.set_ylim(0, 1)
    ax.axis("off")
    W, H, Y = 0.228, 0.97, 0.015
    xs = [0.0, 0.257, 0.514, 0.772]
    lab = {0: "no", 1: "yes"}
    mono = dict(family="monospace", size=5.9)
    tab = [(f"{'row':>4}{'LOC':>5}{'CC':>4}{'defect':>7}", dict(mono, color=INK2))]
    for r in rows:
        v = X.iloc[r]
        tab.append((f"{r:>4}{int(v[cols[0]]):>5}{int(v[cols[1]]):>4}{lab[int(y[r])]:>7}",
                    dict(mono, color=COL["standard"] if r in grp else INK)))
    tab.append((f"Rows {grp[0]}, {grp[1]}, {grp[2]}: 3 of {gsize:,}", dict(color=COL["standard"])))
    tab.append(("identical modules.", dict(color=COL["standard"])))
    tab.append((f"Row {single} has no copy.", {}))
    tab.append((f"{100 * tc['repeated_row_share']:.0f}% of rows have a copy.", {}))
    box(ax, xs[0], Y, W, H, "Data (NASA mc1)", tab, INK2)
    box(ax, xs[1], Y, W, H, "1  Check (no model)", [
        ("Test rows seen in training:", {}), (f"{100 * tc['exposure']:.0f}%   (Eq. 2)", {"weight": "bold"}),
        ("...with the same label:", {}), (f"{100 * tc['pure_exposure']:.0f}%   (Eq. 2b)", {"weight": "bold"}),
        ("Worst-case gap, new cases:", {}), (f"{100 * tc['predicted_gap']:+.0f} pp   (Eq. 3)", {"weight": "bold"}),
        ("", {}), ("FIX RECOMMENDED", {"color": COL["fix"], "weight": "bold"})], COL["standard"])
    box(ax, xs[2], Y, W, H, "2  Fix", [
        ("Train any model as usual.", {}), ("Calibrate seen and new", {}),
        ("rows separately:", {}),
        (f"one threshold: {ex['standard']:.3f}", {"color": COL["standard"]}),
        (f"seen: {ex['fixed_seen']:.3f}  new: {ex['fixed_new']:.3f}", {"color": COL["fix"], "weight": "bold"}),
        ("", {}), ("Valid for any mix of seen", {}), ("and new cases (Prop. 3).", {})], COL["fix"])
    m6 = dict(family="monospace", size=5.9)
    box(ax, xs[3], Y, W, H, "3  Report", [
        ("Coverage (%), target 90", {}),
        (f"{'':<5}{'all':>5}{'seen':>5}{'new':>5}", dict(m6, color=INK2)),
        (f"{'std':<5}{100 * tm.loc['standard', 'coverage_all']:>5.1f}{100 * tm.loc['standard', 'coverage_seen']:>5.1f}"
         f"{100 * tm.loc['standard', 'coverage_new']:>5.1f}", dict(m6, color=COL["standard"])),
        (f"{'fix':<5}{100 * tm.loc['exact', 'coverage_all']:>5.1f}{100 * tm.loc['exact', 'coverage_seen']:>5.1f}"
         f"{100 * tm.loc['exact', 'coverage_new']:>5.1f}", dict(m6, color=COL["fix"], weight="bold")),
        ("Empty sets, new cases:", {}),
        (f"{100 * tm.loc['standard', 'empty_new']:.0f}%  ->  {100 * tm.loc['exact', 'empty_new']:.0f}%", {"weight": "bold"}),
        ("", {}), ("Report new-case coverage.", {})], INK2)
    for i in range(3):
        arrow(ax, xs[i] + W + 0.004, xs[i + 1] - 0.004, Y + H / 2)
    # overflow check: every text must lie inside its box (in display coordinates)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    bad = 0
    for (x, y, w, h), texts in BOXES:
        (bx0, by0), (bx1, by1) = ax.transData.transform([(x, y), (x + w, y + h)])
        for t in texts:
            e = t.get_window_extent(r)
            if e.x1 > bx1 - 1 or e.x0 < bx0 or e.y0 < by0:
                bad += 1
                print("OVERFLOW:", repr(t.get_text()))
    print("text elements checked:", sum(len(t) for _, t in BOXES), "overflows:", bad)
    save(fig, "fig_schematic")


if __name__ == "__main__":
    main()
