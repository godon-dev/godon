#!/usr/bin/env python3
"""make_figs.py -- paper figures for P4 (readable-by-design).

Emits five SVGs into src/ using ONLY the elements svg2pdf.py renders
(rect, line, path M/L/z, circle, text -- no markers, no groups, no
transforms). Data sources: the evidence bundles' card JSONs (event
timestamps), the documented battery numbers (engine-status, via the
evidence generators), and the D2 closeout bracket. Where a run was
purged before bundling, the lane says so and cites the flight log.
"""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
ROOT = os.path.dirname(os.path.dirname(HERE))  # papers/steering/
EV = os.path.join(ROOT, "evidence")
os.makedirs(SRC, exist_ok=True)

def svg_open(W, H, title):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W//2}" y="30" font-size="17" fill="#222" text-anchor="middle" font-weight="bold">{title}</text>']
    return s

def save(name, s):
    s.append("</svg>")
    open(os.path.join(SRC, name), "w").write("\n".join(s) + "\n")
    print(name, "written")

def box(s, x, y, w, h, label, fill="#eef4fb", stroke="#3a6ea5"):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    lines = label.split("\n")
    y0 = y + h/2 - 6*(len(lines)-1) + 4
    for i, ln in enumerate(lines):
        s.append(f'<text x="{x+w/2:.0f}" y="{y0 + i*15:.0f}" font-size="13" fill="#222" text-anchor="middle">{ln}</text>')

def arrow(s, x1, y1, x2, y2, color="#555", label="", ldy=-8):
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"/>')
    import math as _m
    ang = _m.atan2(y2-y1, x2-x1); L=11; a1=ang-_m.radians(153); a2=ang+_m.radians(153)
    hx1, hy1 = x2+L*_m.cos(a1), y2+L*_m.sin(a1); hx2, hy2 = x2+L*_m.cos(a2), y2+L*_m.sin(a2)
    s.append(f'<path d="M {x2:.0f},{y2:.0f} L {hx1:.0f},{hy1:.0f} L {hx2:.0f},{hy2:.0f} z" fill="{color}"/>')
    if label:
        s.append(f'<text x="{(x1+x2)/2:.0f}" y="{(y1+y2)/2+ldy:.0f}" font-size="11" fill="{color}" text-anchor="middle">{label}</text>')

# ---------------------------------------------------------------- fig: loop
def fig_loop():
    s = svg_open(940, 440, "The keeping loop: one promise's life on a live substrate")
    y1, y2, bh, bw = 84, 250, 52, 180
    box(s, 40,  y1, bw, bh, "PROMISE DECLARED\n(a band on a reading)", "#fff8e1", "#b35900")
    box(s, 280, y1, bw, bh, "COMPILED AGAINST\nTHE MEASURED MAP")
    box(s, 520, y1, bw, bh, "THE KEEPER ACTS\n(one dial, once)")
    box(s, 740, y1, 160, bh, "JUDGED,\nLINE BY LINE")
    box(s, 740, y2, 160, bh, "READING LEAVES\nITS BAND", "#fdecea", "#c62828")
    box(s, 500, y2, bw, bh, "MISSES ACCUMULATE\nINTO A CONVICTION", "#fdecea", "#c62828")
    box(s, 270, y2, bw, bh, "THE MAP RE-MEASURES\nTHE MOVED REGION", "#f3e5f5", "#795548")
    box(s, 40,  y2, bw, bh, "RE-SERVED\n(a watering)", "#eef7ee", "#2e7d32")
    arrow(s, 220, y1+bh/2, 280, y1+bh/2)
    arrow(s, 460, y1+bh/2, 520, y1+bh/2)
    arrow(s, 700, y1+bh/2, 740, y1+bh/2)
    arrow(s, 820, y1+bh, 820, y2, "#c62828", "the world moved", 0)
    arrow(s, 740, y2+bh/2, 680, y2+bh/2, "#c62828")
    arrow(s, 500, y2+bh/2, 450, y2+bh/2, "#795548")
    arrow(s, 270, y2+bh/2, 220, y2+bh/2, "#795548")
    arrow(s, 130, y2, 130, y1+bh, "#2e7d32", "next round", 0)
    s.append(f'<text x="740" y="{y1-12}" font-size="12" fill="#2e7d32" text-anchor="end">in band: the verdict is KEPT, no move needed - the loop rests</text>')
    s.append('<text x="40" y="380" font-size="12" fill="#666">Green: the kept path. Red/brown: the repair path the drift forces. Every arrow above is receipted in Section 5.</text>')
    s.append('<text x="40" y="400" font-size="12" fill="#666">Public words only: promise, band, round, watering.</text>')
    save("loop.svg", s)

# -------------------------------------------------------------- fig: strips
# (strips figure removed v2.15 — the seeds table carries repetition)


# ------------------------------------------------------------ fig: renewal
# (merged into fig_broken_promise as its lower panel)
def fig_renewal():
    pass

# ---------------------------------------------------- fig: broken promise
# rows on ONE shared scale: (label, predicted, bar, delivered)
PTS = [
    ("steering, the boundary miss", 0.6486, 0.010, 0.5685),
    ("drift alarm, run 19", 0.0033, 0.0033, 0.2133),
    ("drift alarm, run 21", 0.0033, 0.0033, 0.2433),
    ("drift alarm, run 20", 0.0033, 0.0033, 1.0566),
]

def fig_broken_promise():
    W, H = 940, 640
    s = svg_open(W, H, "How drift impacts a promise")
    L, R = 110, 40
    def x(t): return L + t / 100 * (W - L - R)
    T1, B1 = 90, 300
    T2, B2 = 350, 560
    # TOP panel: the reading against its promised band
    LO, HI = 0.86, 1.30
    def y1(v): return B1 - (v - LO) / (HI - LO) * (B1 - T1)
    s.append(f'<rect x="{L}" y="{y1(1.05):.0f}" width="{W-L-R}" height="{y1(0.95)-y1(1.05):.0f}" fill="#2e7d32" fill-opacity="0.15" stroke="#2e7d32" stroke-width="1" stroke-dasharray="3 3"/>')
    s.append(f'<text x="{L+12}" y="{y1(1.05)+16:.0f}" font-size="13" fill="#2e7d32">the promised band</text>')
    for v in (0.9, 1.0, 1.1, 1.2):
        s.append(f'<line x1="{L}" y1="{y1(v):.0f}" x2="{W-R}" y2="{y1(v):.0f}" stroke="#eeeeee"/>')
        s.append(f'<text x="{L-8}" y="{y1(v)+4:.0f}" font-size="12" fill="#666" text-anchor="end">{v:.1f}</text>')
    s.append(f'<text x="26" y="{(T1+B1)//2}" font-size="13" fill="#444">the reading</text>')
    path1 = [(0,1.00),(30,1.00),(31,1.02),(33,1.12),(36,1.20),(42,1.21),(50,1.18),(54,1.10),(58,1.04),(66,1.01),(100,1.00)]
    s.append('<path d="M ' + " L ".join(f"{x(t):.0f},{y1(v):.0f}" for t,v in path1) + '" fill="none" stroke="#3a6ea5" stroke-width="3"/>')
    s.append(f'<text x="{x(14):.0f}" y="{y1(0.97):.0f}" font-size="13" fill="#555" text-anchor="middle">quiet</text>')
    s.append(f'<text x="{x(40):.0f}" y="{y1(1.27):.0f}" font-size="13" fill="#b35900" text-anchor="middle">the alarm</text>')
    s.append(f'<text x="{x(76):.0f}" y="{y1(1.05)-8:.0f}" font-size="13" fill="#2e7d32" text-anchor="middle">re-landed</text>')
    # BOTTOM panel: the map's error against the answer key
    EMAX = 0.32
    def y2(e): return B2 - e / EMAX * (B2 - T2)
    for e, lab in [(0.0,"0"),(0.1,"0.1"),(0.2,"0.2"),(0.3,"0.3")]:
        s.append(f'<line x1="{L}" y1="{y2(e):.0f}" x2="{W-R}" y2="{y2(e):.0f}" stroke="#eeeeee"/>')
        s.append(f'<text x="{L-8}" y="{y2(e)+4:.0f}" font-size="12" fill="#666" text-anchor="end">{lab}</text>')
    s.append(f'<text x="26" y="{(T2+B2)//2}" font-size="13" fill="#444">map error</text>')
    path2 = [(0,0.02),(30,0.02),(32,0.16),(36,0.27),(48,0.28),(52,0.09),(58,0.035),(70,0.025),(100,0.02)]
    s.append('<path d="M ' + " L ".join(f"{x(t):.0f},{y2(e):.0f}" for t,e in path2) + '" fill="none" stroke="#3a6ea5" stroke-width="3"/>')
    s.append(f'<text x="{x(44):.0f}" y="{y2(0.31):.0f}" font-size="13" fill="#3a6ea5" text-anchor="middle">stale</text>')
    s.append(f'<text x="{x(78):.0f}" y="{y2(0.06):.0f}" font-size="13" fill="#2e7d32" text-anchor="middle">error collapses</text>')
    # shared event lines spanning both panels
    s.append(f'<line x1="{x(31):.0f}" y1="{T1-4}" x2="{x(31):.0f}" y2="{B2}" stroke="#c62828" stroke-width="2" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{x(31)+8:.0f}" y="64" font-size="13" fill="#c62828">the world moves</text>')
    s.append(f'<line x1="{x(52):.0f}" y1="{T1-4}" x2="{x(52):.0f}" y2="{B2}" stroke="#795548" stroke-width="1.5" stroke-dasharray="4 4"/>')
    s.append(f'<text x="{x(52)+8:.0f}" y="78" font-size="13" fill="#795548">re-measured</text>')
    # time axis
    s.append(f'<line x1="{L}" y1="{B2}" x2="{W-R}" y2="{B2}" stroke="#999999" stroke-width="1.5"/>')
    for t in (0, 25, 50, 75, 100):
        s.append(f'<line x1="{x(t):.0f}" y1="{B2-6}" x2="{x(t):.0f}" y2="{B2+6}" stroke="#999999"/>')
    s.append(f'<text x="{(L+W-R)//2}" y="{B2+26}" font-size="13" fill="#444" text-anchor="middle">time (one run\'s life)</text>')
    s.append(f'<text x="16" y="{H-8}" font-size="12" fill="#888">Schematic of the documented battery arc (Section 5.3).</text>')
    save("broken_promise.svg", s)

# ------------------------------------------------------------- fig: bracket
def fig_bracket():
    W, H = 940, 330
    s = svg_open(W, H, "The kept fraction over four hours: luck, keeper, hindsight")
    L, R, B = 250, 110, 70
    def x(v): return L + v * (W - L - R)
    rows = [
        ("doing nothing (luck)", 0.013, "#c62828", True),
        ("what we tended", 0.874, "#2e7d32", True),
        ("perfect hindsight", 1.000, "#795548", False),
    ]
    y = 92
    for name, v, c, filled in rows:
        s.append(f'<text x="16" y="{y+5:.0f}" font-size="15" fill="#333">{name}</text>')
        if name == "perfect hindsight":
            s.append(f'<text x="16" y="{y+23:.0f}" font-size="11" fill="#999">computed after the fact, never flown</text>')
        s.append(f'<line x1="{L}" y1="{y}" x2="{W-40}" y2="{y}" stroke="#dddddd" stroke-width="1.5"/>')
        if filled:
            s.append(f'<circle cx="{x(v):.0f}" cy="{y}" r="11" fill="{c}"/>')
        else:
            s.append(f'<circle cx="{x(v):.0f}" cy="{y}" r="10" fill="white" stroke="{c}" stroke-width="3.5"/>')
        s.append(f'<text x="{x(v)+18:.0f}" y="{y+6:.0f}" font-size="16" fill="{c}" font-weight="bold">{v:.3f}</text>')
        y += 58
    # axis
    ay = 246
    s.append(f'<line x1="{L}" y1="{ay}" x2="{W-40}" y2="{ay}" stroke="#999999" stroke-width="1.5"/>')
    for v, lab in [(0.0,"0"),(0.25,"0.25"),(0.5,"0.5"),(0.75,"0.75"),(1.0,"1.0")]:
        s.append(f'<line x1="{x(v):.0f}" y1="{ay-6}" x2="{x(v):.0f}" y2="{ay+6}" stroke="#999999"/>')
        s.append(f'<text x="{x(v):.0f}" y="{ay+24}" font-size="12" fill="#666" text-anchor="middle">{lab}</text>')
    s.append(f'<text x="16" y="{H-8}" font-size="12" fill="#555">No external keeper appears; the two anchors make the keeper\'s number readable on its own (Section 4).</text>')
    save("bracket.svg", s)

# ------------------------------------------------------------- fig: connectome
def fig_connectome():
    W, H = 940, 340
    s = svg_open(W, H, "The connectome and the corridor")
    cy = 176
    nodes = [(170, "node 1", "the dial"), (470, "node 3", None), (790, "node 2", "the reading")]
    R = 56
    for cx, name, sub in nodes:
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#eef4fb" stroke="#3a6ea5" stroke-width="2.5"/>')
        s.append(f'<text x="{cx}" y="{cy - (6 if sub else -5)}" font-size="15" fill="#222" text-anchor="middle" font-weight="bold">{name}</text>')
        if sub:
            s.append(f'<text x="{cx}" y="{cy + 16}" font-size="12" fill="#556" text-anchor="middle">{sub}</text>')
    # the dial glyph feeding node 1
    s.append(f'<circle cx="70" cy="{cy}" r="15" fill="white" stroke="#b35900" stroke-width="2.5"/>')
    s.append(f'<line x1="70" y1="{cy}" x2="80" y2="{cy-9}" stroke="#b35900" stroke-width="2.5"/>')
    s.append(f'<text x="70" y="{cy+38}" font-size="11" fill="#b35900" text-anchor="middle">the dial</text>')
    s.append(f'<line x1="86" y1="{cy}" x2="{170-R-2}" y2="{cy}" stroke="#b35900" stroke-width="2.5"/>')
    # the corridor edges: node1 -> node3 -> node2, green, proper arrowheads
    def edge(x1, x2, stage):
        s.append(f'<line x1="{x1}" y1="{cy}" x2="{x2-18}" y2="{cy}" stroke="#2e7d32" stroke-width="4"/>')
        s.append(f'<path d="M {x2},{cy} L {x2-18},{cy-8} L {x2-18},{cy+8} z" fill="#2e7d32"/>')
        s.append(f'<text x="{(x1+x2)/2:.0f}" y="{cy+30}" font-size="12" fill="#2e7d32" text-anchor="middle">{stage}</text>')
    edge(170 + R + 4, 470 - R - 4, "stage 1")
    edge(470 + R + 4, 790 - R - 4, "stage 2")
    # the measured-response glyph above each edge (straight-segment wiggle, ±bar)
    def glyph(xm):
        pts = [(xm-34, cy-46), (xm-22, cy-72), (xm-8, cy-24), (xm+6, cy-72), (xm+20, cy-24), (xm+34, cy-46)]
        s.append('<path d="M ' + " L ".join(f"{px},{py}" for px, py in pts) + '" fill="none" stroke="#8899aa" stroke-width="2"/>')
        s.append(f'<line x1="{xm-30}" y1="{cy-84}" x2="{xm+30}" y2="{cy-84}" stroke="#8899aa" stroke-width="1.5" stroke-dasharray="3 3"/>')
        s.append(f'<text x="{xm}" y="{cy-94}" font-size="11" fill="#667" text-anchor="middle">measured: response curve and error bar</text>')
    glyph(320); glyph(630)
    s.append(f'<text x="470" y="{cy+72}" font-size="13" fill="#2e7d32" text-anchor="middle">the corridor: one dial, two hops, to the promised reading</text>')
    s.append(f'<text x="16" y="{H-8}" font-size="12" fill="#555">The connectome: every coupling edge measured (curve and error bar, prior work). The promise steers through it.</text>')
    save("connectome.svg", s)

# ------------------------------------------------------------- fig: refusal
def fig_refusal():
    W, H = 940, 300
    s = svg_open(W, H, "The refusal, in numbers")
    L, R, AXY = 90, 90, 150
    def x(v): return L + v / 0.72 * (W - L - R)
    s.append(f'<line x1="{L}" y1="{AXY}" x2="{W-R}" y2="{AXY}" stroke="#999999" stroke-width="1.5"/>')
    for v in (0.0, 0.2, 0.4, 0.6):
        s.append(f'<line x1="{x(v):.0f}" y1="{AXY-6}" x2="{x(v):.0f}" y2="{AXY+6}" stroke="#999999"/>')
        s.append(f'<text x="{x(v):.0f}" y="{AXY+26}" font-size="12" fill="#666" text-anchor="middle">{v:.1f}</text>')
    # measured reach
    s.append(f'<line x1="{x(0):.0f}" y1="{AXY}" x2="{x(0.1184):.0f}" y2="{AXY}" stroke="#3a6ea5" stroke-width="8" stroke-opacity="0.5"/>')
    s.append(f'<text x="{x(0.06):.0f}" y="{AXY-24}" font-size="13" fill="#3a6ea5" text-anchor="middle">the measured world reaches 0.118</text>')
    # noise gate
    s.append(f'<line x1="{x(0.0514):.0f}" y1="{AXY-12}" x2="{x(0.0514):.0f}" y2="{AXY+12}" stroke="#888888" stroke-width="2"/>')
    s.append(f'<text x="{x(0.0514):.0f}" y="{AXY+46}" font-size="11" fill="#888" text-anchor="middle">noise gate 0.051</text>')
    # the demand
    s.append(f'<path d="M {x(0.6363):.0f},{AXY-30} L {x(0.6363):.0f},{AXY+30}" stroke="#c62828" stroke-width="3"/>')
    s.append(f'<path d="M {x(0.6363)-8:.0f},{AXY-30} L {x(0.6363)+8:.0f},{AXY-30}" stroke="#c62828" stroke-width="3"/>')
    s.append(f'<text x="{x(0.6363):.0f}" y="{AXY-42}" font-size="14" fill="#c62828" text-anchor="middle" font-weight="bold">asked: 0.636</text>')
    s.append(f'<text x="{(x(0.1184)+x(0.6363))/2:.0f}" y="{AXY+70}" font-size="13" fill="#c62828" text-anchor="middle">far beyond anything measured --- refused by name, zero actuation</text>')
    s.append(f'<text x="16" y="{H-8}" font-size="12" fill="#555">The refusal receipt: the demanded shift sits far outside the measured reach; the engine declined and touched nothing.</text>')
    save("refusal.svg", s)

# ------------------------------------------------------------- fig: hold (real data)
def fig_hold():
    import json as _json, re as _re, os as _os
    src = _os.path.join(SRC, "d2pp", "strip.log")
    pts = []
    t0 = None
    for ln in open(src):
        parts = ln.split("|")
        if len(parts) < 3 or not parts[1].startswith("{"): continue
        try: d = _json.loads(parts[1])
        except Exception: continue
        if d.get("node_id") != "node-1": continue
        ts = parts[0]
        h = int(ts[11:13]) + int(ts[14:16]) / 60.0
        if t0 is None: t0 = h
        pts.append((h - t0, d["objective_1"]))
    LO, HI = 0.9467, 1.1067
    W, H = 940, 420
    s = svg_open(W, H, "The four-hour hold, as recorded")
    L, R, T, B = 90, 40, 70, 80
    YLO, YHI = 0.62, 1.32
    def x(t): return L + t / 4.1 * (W - L - R)
    def y(v): return (H - B) - (v - YLO) / (YHI - YLO) * (H - T - B)
    s.append(f'<rect x="{L}" y="{y(HI):.0f}" width="{W-L-R}" height="{y(LO)-y(HI):.0f}" fill="#2e7d32" fill-opacity="0.15" stroke="#2e7d32" stroke-width="1" stroke-dasharray="3 3"/>')
    s.append(f'<text x="{L+12}" y="{y(HI)+16:.0f}" font-size="13" fill="#2e7d32">the promised band</text>')
    for v in (0.7, 0.9, 1.1, 1.3):
        s.append(f'<line x1="{L}" y1="{y(v):.0f}" x2="{W-R}" y2="{y(v):.0f}" stroke="#eeeeee"/>')
        s.append(f'<text x="{L-8}" y="{y(v)+4:.0f}" font-size="12" fill="#666" text-anchor="end">{v:.1f}</text>')
    s.append('<path d="M ' + " L ".join(f"{x(t):.0f},{y(v):.0f}" for t, v in pts) + '" fill="none" stroke="#3a6ea5" stroke-width="2"/>')
    sat = 8 + 12/60.0 - (8 + 9/60.0)
    s.append(f'<line x1="{x(sat):.0f}" y1="{T}" x2="{x(sat):.0f}" y2="{H-B}" stroke="#c62828" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s.append(f'<text x="{x(sat)+8:.0f}" y="{T+14}" font-size="12" fill="#c62828">the slide saturates</text>')
    for t in (0, 1, 2, 3, 4):
        s.append(f'<line x1="{x(t):.0f}" y1="{H-B-6}" x2="{x(t):.0f}" y2="{H-B+6}" stroke="#999999"/>')
        s.append(f'<text x="{x(t):.0f}" y="{H-B+24}" font-size="12" fill="#666" text-anchor="middle">{t}h</text>')
    s.append(f'<text x="26" y="{(T+H-B)//2}" font-size="13" fill="#444">the reading</text>')
    s.append(f'<text x="16" y="{H-8}" font-size="12" fill="#555">Recorded samples, one per judged window (the strip log): 159 windows, 139 kept --- the excursions are the edge-riding straddles.</text>')
    save("hold.svg", s)

if __name__ == "__main__":
    fig_loop(); fig_connectome(); fig_refusal(); fig_broken_promise(); fig_bracket(); fig_hold()
