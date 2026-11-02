#!/usr/bin/env python3
"""fig_bracket.py — kept-fraction between the two anchors (no race).

The honest bracket, internal and free: what doing nothing keeps (the
floor — the band is not satisfied by luck under a moving world), and
what re-planning from the answer key could keep (the ceiling, computed
POST-HOC from the /truth recordings — no live arm, ever). The kept wish
reads absolutely between them. Consumes d2-upkeep/ at room close; until
then this renders the skeleton with the D2 slots marked.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 880, 400
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       '<text x="270" y="24" font-size="13" fill="#333">Kept fraction between the two anchors (no race, brackets only)</text>']

T, B, L, R = 60, 60, 100, 40
def x(t): return L + t / 100 * (W - L - R)
def y(f): return (H - B) - f * (H - T - B)

for f, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1.0")]:
    svg.append(f'<line x1="{L}" y1="{y(f):.0f}" x2="{W-R}" y2="{y(f):.0f}" stroke="#eee"/>')
    svg.append(f'<text x="{L-10}" y="{y(f)+3:.0f}" font-size="10" fill="#666" text-anchor="end">{lab}</text>')
svg.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#999"/>')

# anchors (skeleton values; D2 data replaces at close)
svg.append(f'<line x1="{x(8):.0f}" y1="{y(0.02):.0f}" x2="{x(92):.0f}" y2="{y(0.02):.0f}" stroke="#c62828" stroke-width="2"/>')
svg.append(f'<text x="{x(8):.0f}" y="{y(0.02)-8:.0f}" font-size="10" fill="#c62828">doing nothing (band broken by the moving world; ~0 kept)</text>')
svg.append(f'<line x1="{x(8):.0f}" y1="{y(0.93):.0f}" x2="{x(92):.0f}" y2="{y(0.93):.0f}" stroke="#795548" stroke-width="2" stroke-dasharray="6 3"/>')
svg.append(f'<text x="{x(8):.0f}" y="{y(0.93)-8:.0f}" font-size="10" fill="#795548">re-planning from the answer key (post-hoc ceiling)</text>')
svg.append(f'<rect x="{x(30):.0f}" y="{y(0.78):.0f}" width="{x(70)-x(30):.0f}" height="{y(0.55)-y(0.78):.0f}" fill="#2e7d32" fill-opacity="0.25" stroke="#2e7d32"/>')
svg.append(f'<text x="{x(50):.0f}" y="{y(0.66):.0f}" font-size="11" fill="#2e7d32" text-anchor="middle">the kept promise (D2 fills)</text>')

svg.append(f'<text x="{L}" y="{H-28}" font-size="10" fill="#888">Fraction of judged windows inside the promised band, over the whole 6-hour room.</text>')
svg.append(f'<text x="{L}" y="{H-14}" font-size="10" fill="#888">Floor from the same recording with serves withheld; ceiling computed post-hoc from truth (never a live arm).</text>')
svg.append("</svg>")
open(os.path.join(HERE, "bracket.svg"), "w").write("\n".join(svg))
print("bracket.svg written (skeleton; D2 fills at room close)")
