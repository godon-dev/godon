#!/usr/bin/env python3
"""fig_strips.py — timeline strips per room (fig2-class depiction).

One horizontal strip per flight: declared -> planned -> assigned -> judge
windows -> terminal. Repetition visible: the S2 rows side by side. Data
source: the card JSONs in s1-reflight/ and s2-seeds/ (event tsz fields).
Output: strips.svg (hand-rolled SVG, no deps; public words only).
"""
import json, glob, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def load_events(path):
    d = json.load(open(path))
    ev = d.get("events") or []
    out = []
    for e in ev:
        t = e.get("tsz")
        k = e.get("event") or e.get("type")
        if t is None or k is None:
            continue
        det = e.get("detail")
        extra = ""
        if isinstance(det, dict):
            jd = det.get("judged")
            if isinstance(jd, list) and jd:
                j = jd[-1]
                extra = f"{j['kind']} med {j['median']:.3f} -> {j['verdict']}"
            elif "moves" in det:
                extra = f"moves {det['moves']}"
            elif det.get("reason"):
                extra = str(det["reason"])
        out.append((float(t), k, extra))
    return out

ROOMS = [
    ("S1 full-loop (f3704571)", "s1-reflight/S1-trail/card-f3704571.json"),
    ("S2-a landed", None),  # purged room; numbers in notes.md
    ("S2-b missed", "s2-seeds/S2b-trail/card-b5227a05.json"),
    ("S2-c landed", "s2-seeds/S2c-trail/card-3df03505.json"),
    ("S2-d landed", "s2-seeds/S2d-trail/card-a5e10f8b.json"),
    ("S2-e landed", "s2-seeds/S2e-trail/card-4419e05e.json"),
]

rows = []
for label, rel in ROOMS:
    if rel is None:
        rows.append((label, []))
        continue
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        rows.append((label, load_events(p)))
    else:
        rows.append((label, []))

# render
L, R, T, BH, GAP = 240, 40, 30, 26, 14
W = 980
H = T + (BH + GAP) * len(rows) + 60
COLOR = {"declared": "#888", "planned": "#3a6ea5", "assigned": "#3a6ea5",
         "missed": "#b35900", "landed": "#2e7d32", "undecidable": "#9467bd",
         "refused": "#c62828", "replanned": "#b35900", "remeasure": "#795548"}

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">']
svg.append(f'<rect width="{W}" height="{H}" fill="white"/>')
svg.append(f'<text x="{L}" y="20" font-size="13" fill="#333">Promise held per flight: declared &#8594; planned &#8594; judged windows &#8594; verdict (one row per room; repetition visible)</text>')
y = T
for label, ev in rows:
    svg.append(f'<text x="10" y="{y+17}" font-size="11" fill="#333">{label}</text>')
    svg.append(f'<line x1="{L}" y1="{y+BH-8}" x2="{W-R}" y2="{y+BH-8}" stroke="#ccc" stroke-width="1"/>')
    if not ev:
        svg.append(f'<text x="{L+8}" y="{y+12}" font-size="11" fill="#999">(room purged before bundling &#8212; numbers in notes.md)</text>')
    else:
        t0, t1 = ev[0][0], ev[-1][0]
        span = max(t1 - t0, 1e-9)
        for t, k, extra in ev:
            x = L + (t - t0) / span * (W - L - R)
            c = COLOR.get(k, "#555")
            svg.append(f'<line x1="{x:.1f}" y1="{y+BH-16}" x2="{x:.1f}" y2="{y+BH-2}" stroke="{c}" stroke-width="2"/>')
        # verdict marker at the end
        vk = ev[-1][1]
        vc = COLOR.get(vk, "#555")
        svg.append(f'<circle cx="{W-R-2}" cy="{y+BH-9}" r="4" fill="{vc}"/>')
        svg.append(f'<text x="{L+4}" y="{y+9}" font-size="9" fill="#666">{ev[0][1]} t0 .. {vk} (+{span:.0f}s) {ev[-1][2][:44]}</text>')
    y += BH + GAP
# legend
lx = 10; ly = H - 18
for k, c in COLOR.items():
    svg.append(f'<line x1="{lx}" y1="{ly-4}" x2="{lx+14}" y2="{ly-4}" stroke="{c}" stroke-width="2"/>')
    svg.append(f'<text x="{lx+18}" y="{ly}" font-size="10" fill="#555">{k}</text>')
    lx += 20 + 8 * len(k)
svg.append("</svg>")
open(os.path.join(HERE, "strips.svg"), "w").write("\n".join(svg))
print("strips.svg written,", sum(1 for _, e in rows if e), "data rows")
