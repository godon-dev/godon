#!/usr/bin/env python3
"""fig_loop.py — the keeping loop (fig1-class depiction, drawn).

The loop the receipts show: a promise is declared, compiled against the
measured map, served (held), judged per reading window; when the world
moves and the reading leaves its band, misses accumulate into a
conviction, the aimed probe speaks, the map re-measures the moved
region, and the promise is re-served. Public words only: promise, band,
round, watering.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 420
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       '<text x="330" y="28" font-size="14" fill="#333">The keeping loop (one round per watering)</text>']

def box(x, y, w, h, label, fill="#eef4fb", stroke="#3a6ea5"):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/>')
    svg.append(f'<text x="{x+w/2}" y="{y+h/2+4}" font-size="12" fill="#222" text-anchor="middle">{label}</text>')

def arrow(x1, y1, x2, y2, label="", color="#555"):
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5" marker-end="url(#a)"/>')
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        svg.append(f'<text x="{mx}" y="{my-6}" font-size="10" fill="{color}" text-anchor="middle">{label}</text>')

svg.append('<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#555"/></marker></defs>')

box(60, 70, 150, 44, "promise declared<br/>(band on a reading)".replace("<br/>", " "), "#fff8e1", "#b35900")
box(280, 70, 150, 44, "compiled against the<br/>measured map".replace("<br/>", " "))
box(500, 70, 130, 44, "served: the dial holds")
box(690, 70, 130, 44, "judged per window")
box(690, 200, 130, 44, "reading leaves band", "#fdecea", "#c62828")
box(470, 200, 160, 44, "conviction + aimed probe")
box(240, 200, 160, 44, "map re-measures the<br/>moved region".replace("<br/>", " "))
box(60, 200, 120, 44, "re-served (watering)", "#eef7ee", "#2e7d32")

arrow(210, 92, 280, 92)
arrow(430, 92, 500, 92)
arrow(630, 92, 690, 92)
arrow(755, 114, 755, 200, "the world moved")
arrow(690, 222, 630, 222)
arrow(470, 222, 400, 222)
arrow(240, 222, 180, 222)
arrow(120, 200, 120, 114, "next round", "#2e7d32")
arrow(135, 70, 690, 55, "kept: stays in band — verdict per line, no move needed", "#2e7d32")

svg.append(f'<text x="60" y="300" font-size="11" fill="#777">Receipts live per cell: refusal at the unmeasured edge (S4); the composed serve and its judged lines (S1, S2 x5);</text>')
svg.append(f'<text x="60" y="318" font-size="11" fill="#777">rounds and their cost against the quiet stretches between world moves (D2); survival of a declared move (D1, the 2026-11-01 battery).</text>')
svg.append("</svg>")
open(os.path.join(HERE, "loop.svg"), "w").write("\n".join(svg))
print("loop.svg written")
