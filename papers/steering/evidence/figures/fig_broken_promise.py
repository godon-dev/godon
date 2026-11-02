#!/usr/bin/env python3
"""fig_broken_promise.py — predicted (with bars) vs delivered, per receipt.

The broken-promise scatter: |delivered - predicted| against the plan's own
error bar. Sources: f3704571 (today's compose legs) + the 2026-11-01
battery's conviction ratios (documented in engine-status; the 65-300x
receipts). Log-log axes; the diagonal is the 1x line (promise kept within
its bar); points above it are broken-promise multiples.
"""
import os, math

HERE = os.path.dirname(os.path.abspath(__file__))

# (label, bar, |delivered - predicted|, source)
PTS = [
    ("S1 leg A (n3)", 0.0152, abs(0.7541 - 0.6414), "s1-reflight/S1-trail/card-f3704571.json"),
    ("S1 leg B (n2)", 0.0137, abs(0.7575 - 0.6491), "s1-reflight/S1-trail/card-f3704571.json"),
    ("battery room 20 judge", 0.0033, abs(1.0566 - 0.0033), "engine-status 2026-11-01 (D1 battery)"),
    ("battery room 21 judge", 0.0033, 0.24, "engine-status 2026-11-01 (D1 battery, ~7-13x bars)"),
    ("battery room 19 (lineage)", 0.0033, 0.21, "engine-status 2026-11-01 small-hours (room 19)"),
]

W, H = 860, 520
L, R, T, B = 90, 40, 60, 70

def xmap(v):
    lo, hi = 0.001, 1.0
    return L + (math.log10(max(v, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (W - L - R)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       '<text x="240" y="24" font-size="14" fill="#333">Broken promises: deviation from prediction vs the plan&#8217;s own error bar</text>']

# axes: x = bar, y = deviation (both log)
for i, dec in enumerate([-3, -2, -1, 0]):
    x = xmap(10 ** dec)
    svg.append(f'<line x1="{x:.0f}" y1="{T}" x2="{x:.0f}" y2="{H-B}" stroke="#ddd"/>')
    svg.append(f'<text x="{x:.0f}" y="{H-B+18}" font-size="10" fill="#666" text-anchor="middle">1e{dec}</text>')
svg.append(f'<text x="{(L+W-R)//2}" y="{H-10}" font-size="11" fill="#444" text-anchor="middle">promised error bar</text>')
svg.append(f'<text x="16" y="{(T+H-B)//2}" font-size="11" fill="#444" transform="rotate(-90 16 {(T+H-B)//2})" text-anchor="middle">delivered deviation</text>')

def ymap(v):
    lo, hi = 0.001, 1.0
    return (H - B) - (math.log10(max(v, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (H - T - B)

for i, dec in enumerate([-3, -2, -1, 0]):
    y = ymap(10 ** dec)
    svg.append(f'<line x1="{L}" y1="{y:.0f}" x2="{W-R}" y2="{y:.0f}" stroke="#ddd"/>')
    svg.append(f'<text x="{L-8}" y="{y+3:.0f}" font-size="10" fill="#666" text-anchor="end">1e{dec}</text>')

# 1x diagonal (promise kept)
svg.append(f'<line x1="{xmap(0.001):.0f}" y1="{ymap(0.001):.0f}" x2="{xmap(1):.0f}" y2="{ymap(1):.0f}" stroke="#2e7d32" stroke-dasharray="4 3"/>')
svg.append(f'<text x="{xmap(0.02)+4:.0f}" y="{ymap(0.02)-6:.0f}" font-size="10" fill="#2e7d32">kept within bar (1x)</text>')

for label, bar, dev, src in PTS:
    x, y = xmap(bar), ymap(dev)
    mult = dev / bar
    svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="#b35900" fill-opacity="0.85"/>')
    svg.append(f'<text x="{x+9:.0f}" y="{y+4:.0f}" font-size="10" fill="#555">{label} ({mult:.0f}x)</text>')

svg.append(f'<text x="{L}" y="{T-18}" font-size="10" fill="#888">held-wish legs and judge convictions; multiples = deviation / bar</text>')
svg.append("</svg>")
open(os.path.join(HERE, "broken_promise.svg"), "w").write("\n".join(svg))
print("broken_promise.svg written,", len(PTS), "points")
