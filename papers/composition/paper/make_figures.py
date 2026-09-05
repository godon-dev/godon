#!/usr/bin/env python3
"""Regenerate every figure of paper P3 (composition) from the evidence bundle.

Reads only papers/composition/evidence/ (retained curves, node maps) and
writes papers/composition/paper/figures/*.pdf plus, with --evidence, the
engine-certification PNG/SVG variants into the evidence directory.

One referee rule everywhere (the paper's stated rule):
  sigma_ref = sqrt( sigma_direct^2 + sigma_pred^2 ),
  sigma_pred = sqrt( sigma_map(op point)^2 + (local slope * sigma_input)^2 ),
chained stage by stage; bars at bracketing levels are the max of the flanks
(conservative); z = |direct - pred| / sigma_ref; a point certifies at z < 2.

Planted truth (scenario-cliff, scenario-junction-gate):
  cliff: N1 lin w=1 -0.9-> N2 thr (fires 0.9L/100 > 0.5, i.e. L > 55.56)
         -0.45-> N3 sat w=1 -0.9-> N4 sat w=0; noise sigma = 0.02
  junction: N1 -0.9-> N2 sat relay, N1 -0.9-> N3 thr relay,
            both -0.9-> N4 (w_own = 2, base offset 0.3375 at park)

Usage: python3 make_figures.py [--evidence]
Requires matplotlib (any recent version).
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "..", "evidence")
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)
WANT_EVIDENCE = "--evidence" in sys.argv

BLUE, RED, PURPLE, ORANGE = "#1a6faa", "#c0392b", "#7d3c98", "#e67e22"

# ---------------------------------------------------------------- helpers
def f_sat(x): return x / (1.0 + 4.0 * abs(x - 0.5))
def f_thr(x): return 1.0 if x > 0.5 else 0.0

def ibar(points, x):
    """(value, bar, slope) at x; bracketing segment; bar = max of flanks."""
    pts = sorted(points)
    if len(pts) == 1:
        return pts[0][1], pts[0][2], 0.0
    if x <= pts[0][0]:
        a, b = pts[0], pts[min(1, len(pts) - 1)]
    elif x >= pts[-1][0]:
        a, b = pts[max(0, len(pts) - 2)], pts[-1]
    else:
        for a, b in zip(pts, pts[1:]):
            if a[0] <= x <= b[0]:
                break
    if b[0] == a[0]:
        return a[1], max(a[2], b[2]), 0.0
    t = (x - a[0]) / (b[0] - a[0])
    return (a[1] + t * (b[1] - a[1]), max(a[2], b[2]),
            (b[1] - a[1]) / (b[0] - a[0]))

def interp(points, x):
    return ibar(points, x)[0]

def zref(d, sd, pred, s_pred):
    s = math.sqrt(sd * sd + s_pred * s_pred)
    return abs(d - pred) / max(s, 1e-9)

# ---------------------------------------------------------------- loaders
def load_senders(stem):
    doc = json.load(open(os.path.join(EV, stem + "_final_curves.json")))
    nodes = json.load(open(os.path.join(EV, stem + "_nodes.json")))["nodes"]
    return {s["sender"]: s["curves"] for s in doc["senders"]}, nodes

def load_raw(stem):
    doc = json.load(open(os.path.join(EV, stem + "_curves.json")))
    return doc["curves"], doc["nodes"]

def from_senders(by_sender, nodes, s_node, r_node, channel="objective_0"):
    best = None
    for c in by_sender.get(nodes[s_node], []):
        if c["receiver"] == nodes[r_node] and c["channel"] == channel:
            if best is None or c["num_points"] > best["num_points"]:
                best = c
    return best

def from_raw(curves, nodes, s_node, r_node, channel="objective_0"):
    return from_raw_uuid(curves, nodes[s_node], nodes[r_node], channel)

def from_raw_uuid(curves, s, r, channel="objective_0"):
    best = None
    for c in curves:
        if (c["sender_id"] == s and c["receiver_id"] == r
                and c["channel"] == channel):
            if best is None or c["state"]["num_points"] > best["num_points"]:
                best = c["state"]
    return best

# ---------------------------------------------------------------- cliff fig
def draw_cliff(curves, nodes, get, seed, rid, out_pdf, out_png=None):
    P, S3, D, SH = (get(curves, nodes, "node-1", "node-2"),
                    get(curves, nodes, "node-3", "node-3"),
                    get(curves, nodes, "node-1", "node-3"),
                    get(curves, nodes, "node-1", "node-4"))
    piece, self3, ref, hop4 = (sorted(c["points"]) for c in (P, S3, D, SH))

    pl_piece = lambda L: f_thr(0.9 * L / 100.0)
    pl_ref = lambda L: f_sat(0.5 + 0.45 * f_thr(0.9 * L / 100.0)) - f_sat(0.5)
    pl_tail = lambda L: f_sat(L / 100.0) - f_sat(0.5)
    pl_hop4 = lambda L: f_sat(0.9 * f_sat(0.5 + 0.45 * f_thr(0.9 * L / 100.0))) - f_sat(0.45)

    okp = sum(abs(v - pl_piece(L)) / max(bar, 1e-6) < 2 for L, v, bar in piece)
    oksh = sum(abs(v - pl_hop4(L)) / max(bar, 1e-6) < 2 for L, v, bar in hop4)
    okr = 0
    for L, d, sd in ref:
        pv, pb, _ = ibar(piece, L)
        pred, sbar, slope = ibar(self3, 50.0 + 45.0 * pv)
        okr += zref(d, sd, pred, math.sqrt(sbar**2 + (45.0 * slope * pb)**2)) < 2
    lo = [p for p in ref if p[0] < 55.56]
    hi = [p for p in ref if p[0] > 55.56]
    step = (sum(p[1] for p in hi) / len(hi)) - (sum(p[1] for p in lo) / len(lo))
    br = "L{:.0f}-{:.0f}".format(max(p[0] for p in lo), min(p[0] for p in hi))

    Lp = [l / 2 for l in range(0, 201)]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    fig.suptitle(f"Cliff — seed {seed}, run {rid} (live threshold relay)",
                 fontsize=12)

    ax = axes[0][0]
    ax.errorbar([p[0] for p in piece], [p[1] for p in piece],
                yerr=[p[2] for p in piece], fmt="o", ms=4, capsize=2,
                color=BLUE, label=f"measured ({okp}/{len(piece)} within 2σ)")
    ax.plot(Lp, [pl_piece(l) for l in Lp], "-", lw=1.2, color=RED,
            label="planted (fires at L=55.6)")
    ax.axvline(55.56, color="gray", lw=0.7, ls=":", alpha=0.7)
    ax.set_title("The relay: node-1 → node-2 (threshold)")
    ax.set_xlabel("node-1 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    ax = axes[0][1]
    ax.errorbar([p[0] for p in self3], [p[1] for p in self3],
                yerr=[p[2] for p in self3], fmt="o", ms=4, capsize=2,
                color=PURPLE, label="measured self-walk")
    ax.plot(Lp, [pl_tail(l) for l in Lp], "-", lw=1.2, color=RED,
            label="planted saturation")
    ax.set_title("Tail map: node-3 own walk (saturation)")
    ax.set_xlabel("node-3 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    ax = axes[1][0]
    ax.errorbar([p[0] for p in ref], [p[1] for p in ref],
                yerr=[p[2] for p in ref], fmt="o", ms=5, capsize=3,
                color=BLUE, label="direct (banked, node-1 walk)")
    ax.plot(Lp, [interp(self3, 50.0 + 45.0 * interp(piece, l)) for l in Lp],
            "-", lw=1.4, color=ORANGE, label="composed from pieces")
    ax.plot(Lp, [pl_ref(l) for l in Lp], "--", lw=1.2, color=RED,
            label="planted closed form")
    ax.axvline(55.56, color="gray", lw=0.7, ls=":", alpha=0.7)
    ax.set_title(f"THE REFEREE: node-1 → node-3 through the live relay\n"
                 f"{okr}/{len(ref)} within propagated bars; step {step:+.3f} "
                 f"(planted −0.161); flip bracketed {br}")
    ax.set_xlabel("node-1 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    ax = axes[1][1]
    ax.errorbar([p[0] for p in hop4], [p[1] for p in hop4],
                yerr=[p[2] for p in hop4], fmt="o", ms=4, capsize=2,
                color=BLUE, label=f"measured ({oksh}/{len(hop4)} within 2σ)")
    ax.plot(Lp, [pl_hop4(l) for l in Lp], "--", lw=1.2, color=RED,
            label="planted closed form")
    ax.axvline(55.56, color="gray", lw=0.7, ls=":", alpha=0.7)
    ax.set_title("Second hop: node-1 → node-4 (shape row)")
    ax.set_xlabel("node-1 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    for ax in axes.flat:
        ax.grid(alpha=0.25, lw=0.4); ax.set_ylim(-0.62, 1.22)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_pdf); print("wrote", out_pdf)
    if out_png:
        fig.savefig(out_png, dpi=150)
        fig.savefig(out_png.replace(".png", ".svg"))
        print("wrote", out_png, "+ .svg")
    plt.close(fig)

# ------------------------------------------------------------- junction fig
def draw_junction(curves, nodes, get, out_pdf):
    f12 = sorted(get(curves, nodes, "node-1", "node-2")["points"])
    f13 = sorted(get(curves, nodes, "node-1", "node-3")["points"])
    sat = lambda v: v / (1.0 + abs(v - 0.5) * 4.0)
    thr = lambda v: 1.0 if v > 0.5 else 0.0

    # node-4 identity by elimination (walkers bank sender->all curves)
    n123 = {nodes["node-1"], nodes["node-2"], nodes["node-3"]}
    senders = {c["sender_id"] for c in curves}
    cand4 = [nodes["node-4"]] + [
        s for s in senders if s not in n123 and s != nodes["node-4"]
        and from_raw_uuid(curves, s, s)]
    direct = max((from_raw_uuid(curves, nodes["node-1"], u) for u in cand4),
                 key=lambda c: c["num_points"])
    jm = sorted(max((from_raw_uuid(curves, u, u) for u in cand4),
                    key=lambda c: c["num_points"])["points"])

    Lp = [l / 10 for l in range(0, 1001)]
    base_abs = sat(1.0 + 0.9 * sat(0.009 * 50) + 0.9 * thr(0.009 * 50))
    pred_v = []
    for L in Lp:
        v12 = interp(f12, L); v13 = interp(f13, L)
        pred_v.append(interp(jm, (1.0 + 0.9 * v12 + 0.9 * v13 - 0.3375) / 2.0 * 100.0))

    dpts = direct["points"]
    ok = 0; zmax = (0.0, 0)
    for L, d, sd in sorted(dpts):
        v12, b12, _ = ibar(f12, L); v13, b13, _ = ibar(f13, L)
        sch = 0.9 * math.sqrt(b12**2 + b13**2)
        pred, jbar, slope = ibar(jm, (1.0 + 0.9 * v12 + 0.9 * v13 - 0.3375) / 2.0 * 100.0)
        z = zref(d, sd, pred, math.sqrt(jbar**2 + (slope * sch / 2.0 * 100.0)**2))
        ok += z < 2
        if z > zmax[0]: zmax = (z, L)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    fig.suptitle("Junction — seed 46, run 33522428904 (converging paths, "
                 "shared y-axis)", fontsize=12)

    ax = axes[0][0]
    ax.errorbar([p[0] for p in f12], [p[1] for p in f12], yerr=[p[2] for p in f12],
                fmt="o", ms=4, capsize=2, color=BLUE, label="measured")
    ax.plot(Lp, [sat(0.009 * l) - sat(0.009 * 50) for l in Lp], "-", lw=1.2,
            color=RED, label="planted")
    ax.set_title("Path A: node-1 → node-2 (saturation relay)")
    ax.set_xlabel("node-1 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    ax = axes[0][1]
    ax.errorbar([p[0] for p in f13], [p[1] for p in f13], yerr=[p[2] for p in f13],
                fmt="o", ms=4, capsize=2, color=BLUE, label="measured")
    ax.plot(Lp, [thr(0.009 * l) - thr(0.009 * 50) for l in Lp], "-", lw=1.2,
            color=RED, label="planted (step at L=55.6)")
    ax.set_title("Path B: node-1 → node-3 (threshold relay)")
    ax.set_xlabel("node-1 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    ax = axes[1][0]
    ax.errorbar([p[0] for p in jm], [p[1] for p in jm], yerr=[p[2] for p in jm],
                fmt="o", ms=4, capsize=2, color=PURPLE, label="measured self-walk")
    ax.plot(Lp, [sat(2.0 * (d / 100) + 0.3375) - sat(2.0 * 0.5 + 0.3375) for d in Lp],
            "-", lw=1.2, color=RED, label="planted")
    ax.set_title("Junction map: node-4 own walk (dial → display delta)")
    ax.set_xlabel("node-4 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    ax = axes[1][1]
    ax.errorbar([p[0] for p in dpts], [p[1] for p in dpts], yerr=[p[2] for p in dpts],
                fmt="o", ms=5, capsize=3, color=BLUE, label="direct (banked, node-1 walk)")
    ax.plot(Lp, pred_v, "-", lw=1.4, color=ORANGE, label="composed from pieces")
    ax.plot(Lp, [sat(1.0 + 0.9 * sat(0.009 * l) + 0.9 * thr(0.009 * l)) - base_abs
                 for l in Lp], "--", lw=1.2, color=RED, label="planted closed form")
    ax.axvline(55.56, color="gray", lw=0.7, ls=":", alpha=0.7)
    ax.set_title(f"THE REFEREE: node-1 → node-4 through the junction\n"
                 f"{ok}/{len(dpts)} within propagated bars "
                 f"(max z = {zmax[0]:.2f} at L={zmax[1]:.0f})")
    ax.set_xlabel("node-1 dial"); ax.set_ylabel("display delta"); ax.legend(fontsize=8)

    for ax in axes.flat:
        ax.grid(alpha=0.25, lw=0.4); ax.set_ylim(-0.12, 1.05)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_pdf); print("wrote", out_pdf)
    plt.close(fig)

# ---------------------------------------------------------------- main
def main():
    for stem, seed, rid in (("run33968683471", 47, "33968683471"),
                            ("run33974815211", 48, "33974815211")):
        by_sender, nodes = load_senders(stem)
        png = os.path.join(EV, f"cliff_cert_{rid}.png") if WANT_EVIDENCE else None
        draw_cliff(by_sender, nodes, from_senders, seed, rid,
                   os.path.join(FIG, f"fig{'2' if seed == 47 else '3'}_cliff_s{seed}.pdf"),
                   png)

    curves, nodes = load_raw("junction_gate_run33522428904")
    draw_junction(curves, nodes, from_raw, os.path.join(FIG, "fig4_junction_s46.pdf"))

if __name__ == "__main__":
    main()
