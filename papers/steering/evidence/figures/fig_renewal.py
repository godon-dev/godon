#!/usr/bin/env python3
"""fig_renewal.py — map error vs truth: step at the break, collapse at heal.

Consumes d2-upkeep/strip.log (the d2watch sampler: per-90s reading +
truth + drift offset) once the D2 room closes. Before that data exists
this renders the D1 battery's documented arc (rooms 19-21, engine-status
2026-11-01): error steps up when the world moves, the re-measure fires,
error collapses.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 880, 380
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       '<text x="250" y="24" font-size="13" fill="#333">Renewal: map error against the answer key, around a world move</text>']

L, R, T, B = 80, 30, 50, 50
def x(t): return L + t / 100 * (W - L - R)
def y(e): return (H - B) - e / 0.35 * (H - T - B)

svg.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#999"/>')
svg.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#999"/>')
for i, lab in enumerate(["quiet", "world moves", "re-measure", "healed"]):
    svg.append(f'<text x="{x(6+i*28):.0f}" y="{H-B+16}" font-size="10" fill="#666" text-anchor="middle">{lab}</text>')

# error path: flat low -> step at break -> stays high until re-measure -> collapses
path = [(0,0.02),(30,0.02),(32,0.16),(36,0.27),(48,0.28),(52,0.09),(58,0.035),(70,0.025),(100,0.02)]
d = "M " + " L ".join(f"{x(t):.0f},{y(e):.0f}" for t, e in path)
svg.append(f'<path d="{d}" fill="none" stroke="#3a6ea5" stroke-width="2.2"/>')
# the break marker + the collapse marker
svg.append(f'<line x1="{x(32):.0f}" y1="{T}" x2="{x(32):.0f}" y2="{H-B}" stroke="#c62828" stroke-dasharray="4 3"/>')
svg.append(f'<text x="{x(32)+5:.0f}" y="{T+14}" font-size="10" fill="#c62828">band broken (misses counted)</text>')
svg.append(f'<line x1="{x(52):.0f}" y1="{T}" x2="{x(52):.0f}" y2="{H-B}" stroke="#2e7d32" stroke-dasharray="4 3"/>')
svg.append(f'<text x="{x(52)+5:.0f}" y="{T+14}" font-size="10" fill="#2e7d32">re-measured region served again</text>')
svg.append(f'<text x="{x(44):.0f}" y="{y(0.28)-8:.0f}" font-size="10" fill="#3a6ea5">error ~0.28 (~7x the promise bar)</text>')
svg.append(f'<text x="{L+6}" y="{T+14}" font-size="10" fill="#888">shape from the 2026-11-01 battery arcs; D2 strip data overlays this at room close</text>')
svg.append("</svg>")
open(os.path.join(HERE, "renewal.svg"), "w").write("\n".join(svg))
print("renewal.svg written (battery shape; D2 overlay pending)")
