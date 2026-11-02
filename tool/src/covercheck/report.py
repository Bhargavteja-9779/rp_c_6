"""Self-contained HTML report: the check, the verdict and measured coverage with and without the fix."""
from __future__ import annotations

import html

import pandas as pd

from .check import CheckResult

_CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:860px;margin:32px auto;padding:0 16px;
color:#1b1b1a;background:#fcfcfb;line-height:1.5}
h1{font-size:1.5rem;margin-bottom:4px}h2{font-size:1.15rem;margin-top:28px}
.sub{color:#52514e;margin-top:0}.verdict{padding:12px 16px;border-radius:8px;font-weight:600;margin:16px 0}
.fix{background:#fdecea;border-left:4px solid #c0392b}.adv{background:#fff4e0;border-left:4px solid #d68910}
.ok{background:#e8f6ee;border-left:4px solid #1e8449}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:right;padding:6px 8px;border-bottom:1px solid #e4e3df}th:first-child,td:first-child{text-align:left}
.kpi{display:flex;gap:12px;flex-wrap:wrap}.kpi div{flex:1;min-width:150px;border:1px solid #e4e3df;border-radius:8px;
padding:10px 12px}.kpi b{display:block;font-size:1.4rem}.note{color:#52514e;font-size:.9rem}
"""


def _bars(summary: pd.DataFrame, alpha: float) -> str:
    """Inline SVG: coverage of all / seen / new cases for each mode, with the target line."""
    cols = [("coverage_all", "All test cases"), ("coverage_seen", "Seen cases"), ("coverage_new", "New cases")]
    modes = list(summary.index)
    colors = {"standard": "#2a78d6", "exact": "#eb6834", "distance": "#1baf7a"}
    names = {"standard": "Standard", "exact": "Fixed (seen/new)", "distance": "Fixed (distance)"}
    W, H, top, left, bw = 640, 230, 20, 40, 34
    lo = max(0.0, min(0.5, float(summary[[c for c, _ in cols]].min().min()) - 0.05))
    y = lambda v: top + (1 - (v - lo) / (1 - lo)) * (H - top - 40)
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Coverage by case type">']
    for t in (lo, (lo + 1) / 2, 1.0):
        out.append(f'<line x1="{left}" x2="{W}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="#e4e3df"/>'
                   f'<text x="{left - 6}" y="{y(t) + 4:.1f}" font-size="11" text-anchor="end" fill="#52514e">{100 * t:.0f}%</text>')
    gw = (W - left) / len(cols)
    for i, (c, lab) in enumerate(cols):
        x0 = left + i * gw + (gw - bw * len(modes) - 4 * (len(modes) - 1)) / 2
        for j, m in enumerate(modes):
            v = summary.loc[m, c]
            if pd.isna(v):
                continue
            x = x0 + j * (bw + 4)
            out.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw}" height="{y(lo) - y(v):.1f}" rx="4" fill="{colors.get(m, "#888")}">'
                       f'<title>{names.get(m, m)}, {lab}: {100 * v:.1f}%</title></rect>'
                       f'<text x="{x + bw / 2:.1f}" y="{y(v) - 4:.1f}" font-size="10" text-anchor="middle" fill="#1b1b1a">{100 * v:.1f}</text>')
        out.append(f'<text x="{left + i * gw + gw / 2:.1f}" y="{H - 18}" font-size="12" text-anchor="middle" fill="#1b1b1a">{lab}</text>')
    t = y(1 - alpha)
    out.append(f'<line x1="{left}" x2="{W}" y1="{t:.1f}" y2="{t:.1f}" stroke="#1b1b1a" stroke-dasharray="4 3"/>'
               f'<text x="{W}" y="{t - 4:.1f}" font-size="11" text-anchor="end" fill="#1b1b1a">target {100 * (1 - alpha):.0f}%</text>')
    lx = left
    for m in modes:
        out.append(f'<rect x="{lx}" y="{H - 12}" width="10" height="10" rx="2" fill="{colors.get(m, "#888")}"/>'
                   f'<text x="{lx + 14}" y="{H - 3}" font-size="11" fill="#1b1b1a">{names.get(m, m)}</text>')
        lx += 150
    return "".join(out) + "</svg>"


def html_report(title: str, chk: CheckResult, summary: pd.DataFrame | None = None, task: str = "classification") -> str:
    cls = "fix" if chk.verdict.startswith("FIX REC") else ("adv" if chk.verdict.startswith("FIX ADV") else "ok")
    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>CoverCheck report</title><style>{_CSS}</style></head><body>",
             f"<h1>CoverCheck report</h1><p class='sub'>{html.escape(title)} · target coverage {100 * (1 - chk.alpha):.0f}%</p>",
             "<h2>1. Check (no model needed)</h2><div class='kpi'>",
             f"<div>Rows with an identical copy<b>{100 * chk.repeated_row_share:.1f}%</b></div>",
             f"<div>Test rows seen in training<b>{100 * chk.exposure:.1f}%</b></div>",
             f"<div>…with the same label<b>{100 * chk.pure_exposure:.1f}%</b></div>",
             f"<div>Predicted worst-case gap<b>{100 * chk.predicted_gap:+.1f} pp</b></div></div>",
             f"<div class='verdict {cls}'>{html.escape(chk.verdict)}</div><ul>"]
    parts += [f"<li>{html.escape(r)}</li>" for r in chk.reasons]
    parts.append("</ul>")
    if summary is not None:
        parts.append("<h2>2–3. Fix and report (measured on random splits)</h2>")
        parts.append(_bars(summary, chk.alpha))
        size_lab = "Mean set size, new cases" if task == "classification" else "Mean interval width, new cases"
        parts.append("<table><tr><th>Method</th><th>All cases</th><th>Seen cases</th><th>New cases</th>"
                     f"<th>{size_lab}</th>" + ("<th>Empty sets, new</th>" if task == "classification" else "") + "</tr>")
        names = {"standard": "Standard split conformal", "exact": "Fixed: seen/new calibrated separately",
                 "distance": "Fixed: calibrated by distance"}
        for m, r in summary.iterrows():
            f = lambda v: "–" if pd.isna(v) else f"{100 * v:.1f}%"
            parts.append(f"<tr><td>{names.get(m, m)}</td><td>{f(r.coverage_all)}</td><td>{f(r.coverage_seen)}</td>"
                         f"<td><b>{f(r.coverage_new)}</b></td><td>{r.size_new:.3g}</td>"
                         + (f"<td>{f(r.empty_new)}</td>" if task == "classification" else "") + "</tr>")
        parts.append("</table><p class='note'>Report the new-case coverage next to the overall figure. "
                     "The overall figure averages over seen cases, which a model can simply look up.</p>")
    parts.append("<p class='note'>Generated by covercheck. Method: check–fix–report for conformal prediction "
                 "on data with repeated rows.</p></body></html>")
    return "".join(parts)
