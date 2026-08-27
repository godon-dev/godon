#!/usr/bin/env python3
"""P2 figure generator: every figure recomputable from evidence/sweep/.
Usage: python3 make_figures.py   (writes papers/characterization/paper/figures/)"""
import json, csv, glob, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "/projects/godon/papers/characterization/evidence/sweep"
OUT = "/projects/godon/papers/characterization/paper/figures"
os.makedirs(OUT, exist_ok=True)

def load(cid):
    d = glob.glob(f"{EVID}/cell-{cid}-*/curves.json")[0]
    raw = json.load(open(d))
    return raw.get("curves", []) if isinstance(raw, dict) else raw

def carrier(cid, ch=0, param="param_1"):
    best = None
    for c in load(cid):
        if c.get("param") != param: continue
        chs = str(c.get("channel", ""))
        chn = int(chs.rsplit("_", 1)[-1]) if chs.rsplit("_", 1)[-1].isdigit() else chs
        if chs and chn != ch: continue
        pts = c.get("state", {}).get("points", [])
        v = max((abs(p[1]) for p in pts), default=0)
        if best is None or v > best[0]: best = (v, pts)
    return sorted(best[1]) if best else []

def truth_fn(base, weight, strength):
    f = {"linear": lambda x: x, "polynomial": lambda x: x*x,
         "threshold": lambda x: 1.0 if x > 0.5 else 0.0,
         "saturation": lambda x: x/(1+4*abs(x-0.5))}[base]
    return lambda L: strength * weight * (f(L/100.0) - f(0.5))

# ── Fig 1: the four shapes, measured vs planted, with bars ──────────
cells = [("a3", "linear", 0.5, 0.7, "Linear"),
         ("a1", "saturation", 1.0, 0.7, "Saturation"),
         ("s2", "threshold", 0.5, 0.7, "Threshold"),
         ("s4", "polynomial", 0.5, 0.7, "Polynomial")]
fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True)
for ax, (cid, base, w, s, title) in zip(axes.flat, cells):
    pts = carrier(cid)
    T = truth_fn(base, w, s)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; es = [p[2] for p in pts]
    lx = [i for i in range(101)]
    ax.plot(lx, [T(x) for x in lx], ":", color="0.55", lw=1.2, label="planted truth")
    ax.errorbar(xs, ys, yerr=es, fmt="o", ms=4.5, color="#1a5fb4", capsize=2.5, lw=1, label="measured")
    ax.set_title(title, fontsize=11)
    ax.set_ylim(-0.45, 0.45)
    ax.axhline(0, color="0.85", lw=0.6)
axes[0,0].set_ylabel("response shift"); axes[1,0].set_ylabel("response shift")
for ax in axes[1]: ax.set_xlabel("parameter level")
axes[0,0].legend(fontsize=8, loc="lower right")
fig.suptitle("Measured response curves vs planted truth (strength 0.7, $\\sigma$=0.02)", fontsize=12)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_shapes.pdf"); plt.close(fig)

# ── Fig 2: envelope — max deviation over strength x noise ──────────
rows = {r[0]: r for r in list(csv.reader(open(f"{EVID}/sweep.csv")))[1:] if r}
import numpy as np
fig, ax = plt.subplots(figsize=(7, 4.2))
strengths = [0.1, 0.2, 0.3, 0.35, 0.5, 0.7, 0.9]
for sigma, marker, cells_s in [(0.02, "o", ["b1","b2","b3","b3x","b4","a3","b5"]),
                                 (0.05, "s", [None,None,None,"n4",None,"n1",None]),
                                 (0.10, "^", [None,None,None,"r3",None,"n2","n3"])]:
    xs, ys = [], []
    for st, cid in zip(strengths, cells_s):
        if cid and cid in rows and rows[cid][8]:
            xs.append(st); ys.append(float(rows[cid][8]))
    if xs: ax.plot(xs, ys, marker=marker, lw=1, ms=6, label=f"$\\sigma$={sigma}")
ax.axhline(2.0, color="crimson", ls="--", lw=1, label="2$\\sigma$ certificate bound")
ax.set_xlabel("coupling strength"); ax.set_ylabel("max deviation [$\\sigma$ units]")
ax.set_title("Calibration envelope: worst-point deviation across conditions")
ax.legend(fontsize=9); ax.set_ylim(0, 2.4)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_envelope.pdf"); plt.close(fig)

# ── Fig 3: levels walked vs strength (effort tracks signal) ─────────
fig, ax = plt.subplots(figsize=(6, 3.8))
pairs = [(0.1,"b1"),(0.2,"b2"),(0.3,"b3"),(0.5,"b4"),(0.7,"a3"),(0.9,"b5")]
ax.plot([p for p,_ in pairs], [int(rows[c][7]) for _,c in pairs], "o-", color="#26a269", ms=6)
for p, c in pairs: ax.annotate(rows[c][7], (p, int(rows[c][7])), textcoords="offset points", xytext=(0,7), fontsize=8, ha="center")
ax.set_xlabel("coupling strength"); ax.set_ylabel("levels walked")
ax.set_title("Walk depth scales with signal (priced-stop budget allocation)")
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_levels.pdf"); plt.close(fig)

# ── Fig 4: non-stationarity — ns3 wide bars under growing noise ─────
fig, ax = plt.subplots(figsize=(6, 4))
pts = carrier("ns3")
T = truth_fn("saturation", 1.0, 0.7)
lx = [i for i in range(101)]
ax.plot(lx, [T(x) for x in lx], ":", color="0.55", lw=1.2, label="planted truth")
ax.errorbar([p[0] for p in pts], [p[1] for p in pts], yerr=[p[2] for p in pts],
            fmt="o", ms=5, color="#c64600", capsize=3, lw=1.2, label="measured (growing noise)")
# overlay calm-cell bars for contrast
calm = carrier("a1")
ax.errorbar([p[0] for p in calm], [p[1] for p in calm], yerr=[p[2] for p in calm],
            fmt="x", ms=4, color="#1a5fb4", capsize=2, lw=0.8, alpha=0.6, label="measured (calm, a1)")
ax.set_xlabel("parameter level"); ax.set_ylabel("response shift")
ax.set_title("ns3: error bars fatten honestly as noise grows — truth stays inside")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_ns3.pdf"); plt.close(fig)

print("figures written:", sorted(os.listdir(OUT)))
