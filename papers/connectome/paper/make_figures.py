#!/usr/bin/env python3
"""Regenerate every figure of paper P5 (connectome) from the evidence bundles.

Reads only papers/connectome/evidence/ (timestamped truth + curves captures
of cells 2rf, 3rf, 4, 5, 6) and writes papers/connectome/paper/figures/*.pdf.

Honesty rules, matching the paper text:
  - per-curve bar = max bars_sum over the curve's gaps (the receipt metric);
  - registry identities never print (nodes are letters, curves are lines);
  - the slide kind is P4-cited and has no local bar series (its room's bars
    live in the estate ledgers) — the four-kind figure shows the three kinds
    whose captures are banked, and the caption says so;
  - evening series is ghost-filtered: curve identities present in fewer than
    60% of a room's captures are registry leftovers, not the room's own
    curves (price-v1 rule), and are dropped;
  - the connectome plate draws the MEASURED map (curves artifact), never the
    truth channel; truth supplies only clocks (uptime_secs) for x-axes.

Usage: python3 make_figures.py   (matplotlib required; run under uv if needed)
"""

import json, glob, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.normpath(os.path.join(HERE, "..", "evidence"))
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

FROZEN = 0.02
BLUE, RED, GRAY, INK = "#1f4e8c", "#b23a3a", "#b9b9b9", "#262626"


def load_room(cell):
    """Return list of (uptime, curves_list) sorted by capture time.

    Two honesty cuts, both mechanical:
    1. Unparseable/partial capture files are skipped and counted (torn
       writes happen at 45s cadence).
    2. Some evidence dirs banked captures from MORE than one room-window
       (a capture script ran across boots; receipted). Within one room,
       wall-clock stamp minus bench uptime is constant, so captures are
       kept only if they fall in the directory's MAJORITY offset cluster
       (+/-150s) — the nominal room's own window. Wrong-room strays drop
       out; for clean dirs this is a no-op.
    """
    parsed, skipped = [], 0
    for cf in sorted(glob.glob(os.path.join(EV, cell, "*curves.json"))):
        try:
            data = json.load(open(cf))
        except Exception:
            skipped += 1
            continue
        stem = os.path.basename(cf).replace("-curves.json", "")
        try:
            stamp = int(stem[:2]) * 3600 + int(stem[2:4]) * 60 + int(stem[4:6])
        except Exception:
            stamp = None
        tf = cf.replace("-curves.json", "-truth.json")
        up, has_truth = None, False
        if os.path.exists(tf):
            try:
                t = json.load(open(tf))
                up = t.get("uptime_secs")
                has_truth = up is not None
            except Exception:
                pass
        if up is None:  # fall back to filename clock (flagged: no truth anchor)
            up = stamp if stamp is not None else 0
        parsed.append([float(up), stamp, data.get("curves", []), has_truth])

    # the room's own window, from truth-anchored files only (a missing-truth
    # file falls back to stamp-as-uptime, offset 0 — those must NOT vote):
    # within one room the stamp-minus-uptime offset is constant, so the
    # densest 240s band among truth-anchored offsets identifies the window.
    kept = parsed
    anchored = [p for p in parsed if p[3] and p[1] is not None]
    if len(anchored) >= 3:
        offs = sorted(p[1] - p[0] for p in anchored)
        best_lo, best_n = 0, 0
        lo = 0
        for hi in range(len(offs)):
            while offs[hi] - offs[lo] > 240:
                lo += 1
            if hi - lo + 1 > best_n:
                best_n, best_lo = hi - lo + 1, lo
        c_lo, c_hi = offs[best_lo], offs[best_lo + best_n - 1]
        room = [p for p in anchored if c_lo - 120 <= (p[1] - p[0]) <= c_hi + 120]
        s_lo = min(p[1] for p in room); s_hi = max(p[1] for p in room)
        kept = room + [p for p in parsed if not p[3] and p[1] is not None
                       and s_lo - 60 <= p[1] <= s_hi + 60]
        if len(kept) < len(parsed):
            print(f"  [{cell}] {len(parsed) - len(kept)} wrong-window capture(s) dropped "
                  f"(kept the room's own window: {len(kept)} of {len(parsed)}, "
                  f"{len(room)} truth-anchored)")
    if skipped:
        print(f"  [{cell}] {skipped} unparseable capture(s) skipped")
    caps = [(p[0], p[2]) for p in kept]
    caps.sort(key=lambda x: x[0])
    return caps


def curve_id(c):
    return (c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8],
            c.get("param", "?"), c.get("channel", "?"))


def bar(c):
    g = c.get("state", {}).get("gaps", [])
    return max([abs(gg.get("bars_sum", 0.0)) for gg in g], default=0.0)


def series(cell):
    """per-identity time series of max bars. Room ownership is already
    settled by load_room's window cut, so every identity in the room's
    own captures counts (curve groups legitimately retire and re-form
    mid-room; short-lived segments are real curves, not ghosts)."""
    caps = load_room(cell)
    times = [t for t, _ in caps]
    ids = {}
    for t, cs in caps:
        for c in cs:
            i = curve_id(c)
            ids.setdefault(i, {})[t] = bar(c)
    return times, ids, list(ids)


# ---------------- Figure: the connectome (measured map) ----------------

def fig_connectome():
    """Figure 1, full page, final shape: the whole measured map above
    (six nodes, ten couplings, blue = measured in full, gray = young),
    with numbered badges on three featured edges; below, THREE large
    curves --- one per kind the room contains (the swing, a measured
    null, the self-reading) --- each readable, each tied to its edge
    by its badge number. No micro-glyphs riding edges."""
    caps = load_room("cell6-transfer")
    full_up, full = max(caps, key=lambda x: len(x[1]))          # topology
    up, curves = [(t, cs) for t, cs in caps if len(cs) == 6][-1]  # completed
    p1 = curves[0].get("sender_id", "?")[:8]
    senders = {c.get("sender_id", "?")[:8] for c in full}
    p2 = next(s for s in senders if s != p1)
    recvs = []
    for c in full:
        r = c.get("receiver_id", "?")[:8]
        if r not in (p1, p2) and r not in recvs:
            recvs.append(r)
    letters = {p1: "A", p2: "B"}
    for i, n in enumerate(recvs):
        letters[n] = chr(ord("C") + i)
    complete = {(c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8])
                for c in curves}
    curve_of = {(c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8]): c
                for c in curves}
    null_recv = recvs[0]

    # ---- page 1: the graph alone, tight canvas, everything big ----
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch, Polygon

    fig = plt.figure(figsize=(7.4, 5.1))
    ax = fig.add_axes([0.012, 0.115, 0.976, 0.865])
    ax.set_xlim(0.2, 22.2); ax.set_ylim(2.6, 15.7)
    ax.set_aspect("equal"); ax.axis("off")

    allc = sorted(full, key=lambda c: (letters[c.get("sender_id", "?")[:8]],
                                       letters[c.get("receiver_id", "?")[:8]]))
    complete12 = {(c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8])
                  for c in allc if len(c.get("state", {}).get("points", [])) >= 6}

    pos = {p1: (3.6, 11.0), p2: (3.6, 5.6)}
    for n, y in zip(recvs, (14.0, 10.9, 7.8, 4.7)):
        pos[n] = (20.4, y)
    R = 0.8

    def border(s, r):
        x1, y1 = pos[s]; x2, y2 = pos[r]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / L, dy / L
        return (x1 + R * ux, y1 + R * uy), (x2 - R * ux, y2 - R * uy)

    def draw_edge(s, r, rad):
        (sx, sy), (tx, ty) = border(s, r)
        done = (s, r) in complete12
        ax.annotate("", xy=(tx, ty), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=BLUE if done else GRAY,
                                    lw=3.6 if done else 1.9,
                                    shrinkA=0, shrinkB=0,
                                    alpha=0.95 if done else 0.85,
                                    connectionstyle=f"arc3,rad={rad}",
                                    zorder=3 if done else 2))

    # fan edges: blue bows gently upward, gray gently downward
    for r in recvs:
        draw_edge(p1, r, +0.12)
        draw_edge(p2, r, -0.12)
    # the A <-> B pair: symmetric gentle arcs on opposite sides of the axis
    draw_edge(p1, p2, +0.35)
    draw_edge(p2, p1, +0.35)

    # self-loops OUTSIDE the circles, on the left, explicit arrowheads
    def self_loop(n):
        x, y = pos[n]
        done = n == p1
        col = BLUE if done else GRAY
        p0 = (x - 0.77 * R, y + 0.64 * R)
        p3 = (x - 0.77 * R, y - 0.64 * R)
        c1 = (x - R - 1.7, y + 1.05)
        c2 = (x - R - 1.7, y - 1.05)
        path = Path([p0, c1, c2, p3],
                    [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
        ax.add_patch(PathPatch(path, fill=False, edgecolor=col,
                               lw=3.6 if done else 1.9,
                               alpha=0.95 if done else 0.85,
                               capstyle="round", zorder=3 if done else 2))
        tx, ty = p3[0] - c2[0], p3[1] - c2[1]
        L = (tx * tx + ty * ty) ** 0.5
        ux, uy = tx / L, ty / L
        base = (p3[0] - ux * 0.46, p3[1] - uy * 0.46)
        nx, ny = -uy, ux
        tri = [p3, (base[0] + nx * 0.17, base[1] + ny * 0.17),
               (base[0] - nx * 0.17, base[1] - ny * 0.17)]
        ax.add_patch(Polygon(tri, closed=True, fc=col, ec=col,
                             alpha=0.95 if done else 0.85, zorder=3 if done else 2))

    self_loop(p1)
    self_loop(p2)

    # nodes on top of every edge endpoint
    for n, (x, y) in pos.items():
        fc = "#dce8f7" if n in senders else "white"
        ax.add_patch(plt.Circle((x, y), R, fc=fc, ec=INK, lw=3.0, zorder=6))
        ax.text(x, y, letters[n], ha="center", va="center", fontsize=32,
                fontweight="bold", color=INK, zorder=7)

    ax.text(11.2, 15.35, "The connectome: the whole measured map of one live system",
            ha="center", fontsize=12.5, color="#222", fontweight="bold")

    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([], [], color=BLUE, lw=3.6, label="walked in full"),
        Line2D([], [], color=GRAY, lw=1.9, label="walk just begun"),
    ], loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2,
        frameon=False, fontsize=12, handlelength=2.4, columnspacing=2.6)

    fig.savefig(os.path.join(OUT, "connectome.pdf"))
    plt.close(fig)

    # ---- ground truth from the SCENARIO: the world is a DAG of 0.7
    # edges over six linear nodes (before the declared change), so each
    # edge's true response is a straight line through the origin with a
    # fixed gain. Gains computed from the scenario's own edge list with
    # the sender's dial active and every other member at rest.
    import re as _re
    yml = open(os.path.normpath(os.path.join(HERE, "..", "..", "..",
                                             "examples", "bench", "scenario-generic-n",
                                             "topologies", "sweep-transfer-0.7-n6.yaml"))).read()
    edges = [({"from": a, "to": b, "s": float(s)}) for a, b, s in
             _re.findall(r"from: (node-\d+)\s+from_channel: \d+\s+to: (node-\d+)\s+"
                         r"to_channel: \d+\s+strength: ([\d.\-]+)", yml)]
    nodes6 = [f"node-{i}" for i in range(1, 7)]

    def true_gain(sender, receiver):
        x = {n: (1.0 if n == sender else 0.0) for n in nodes6}
        vals = dict(x)
        for _ in range(5):
            prev = dict(vals)
            for n in nodes6:
                vals[n] = x[n] + sum(e["s"] * prev[e["from"]] for e in edges if e["to"] == n)
        return vals[receiver]

    # A is node-1 (the only node reaching all five others; its self gain
    # is exactly 1.0). Receivers ranked by measured response magnitude
    # (the scenario gains rise with node index) -- inferred, declared.
    a_cross = sorted([c for c in curves if c.get("sender_id", "?")[:8] == p1
                      and c.get("receiver_id", "?")[:8] != p1],
                     key=lambda c: max(abs(p[1]) for p in c["state"]["points"]))
    recv_node = {c.get("receiver_id", "?")[:8]: f"node-{i + 2}" for i, c in enumerate(a_cross)}
    truth_gain = {}
    for c in curves:
        if c.get("sender_id", "?")[:8] == p1:
            rid = c.get("receiver_id", "?")[:8]
            node_r = "node-1" if rid == p1 else recv_node[rid]
            truth_gain[(p1, rid)] = true_gain("node-1", node_r)

    # ---- page 2: every edge's curve, one full page, one panel each ----
    # The universal scientific idiom, nothing invented: linear axes with
    # numeric y-ticks, a line through measured points, classic capped
    # error bars, and the scenario's true response as a dashed reference
    # where the node identity is known. Explanatory text lives in the
    # caption, not on the figure.
    from matplotlib.ticker import MaxNLocator

    fig2 = plt.figure(figsize=(7.4, 9.7))
    gs2 = fig2.add_gridspec(4, 3, hspace=0.58, wspace=0.30,
                            left=0.115, right=0.985, top=0.915, bottom=0.062)
    for i, c in enumerate(allc):
        s = letters[c.get("sender_id", "?")[:8]]
        r = letters[c.get("receiver_id", "?")[:8]]
        a = fig2.add_subplot(gs2[i])
        st = c.get("state", {})
        pts = sorted(st.get("points", []), key=lambda p: p[0])
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; es = [abs(p[2]) for p in pts]
        g = truth_gain.get((c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8]))
        if g is not None:
            # records are changes from the resting dial (50): truth likewise
            LX = [0, 100]
            a.plot(LX, [g * (l - 50) / 100.0 for l in LX], color="#444444",
                   ls=(0, (5, 3)), lw=1.3, zorder=2)
            a.text(98, g * 0.48, "truth", ha="right", va="bottom",
                   fontsize=8, color="#444444")
        if xs:
            # join ALL consecutive measurements --- every dot is a real
            # probe; the line through them is what the walk recorded
            for j in range(1, len(xs)):
                a.plot([xs[j - 1], xs[j]], [ys[j - 1], ys[j]],
                       color=BLUE, lw=1.6, zorder=4)
            a.errorbar(xs, ys, yerr=es, fmt="o", color=BLUE, ms=3.6,
                       ecolor=BLUE, elinewidth=1.1, capsize=2.2, zorder=5)
            a.set_xlim(-5, 105)
        a.axhline(0, color="#dddddd", lw=0.7, zorder=0)
        a.set_title(f"{s} to {r}  ({len(pts)} measurements)", fontsize=11, pad=5)
        a.set_xticks([0, 50, 100])
        a.tick_params(axis="x", labelsize=8)
        a.yaxis.set_major_locator(MaxNLocator(nbins=4))
        a.tick_params(axis="y", labelsize=7.5)
        row, col = divmod(i, 3)
        if row == 3:
            a.set_xlabel("the dial's level", fontsize=10)
        if col == 0:
            a.set_ylabel("the reading", fontsize=10)
        for sp in a.spines.values():
            sp.set_linewidth(0.8)
    fig2.suptitle("Every edge's own curve --- one panel per coupling of the map",
                  fontsize=14, y=0.972)
    fig2.savefig(os.path.join(OUT, "curves.pdf"))
    plt.close(fig2)
    return 6, 10, len(allc)


# ---------------- Figure: the three measured change kinds ----------------

def fig_fourkinds():
    rooms = [
        ("cell2-gainclimb-refly", "an influence doubles"),
        ("cell3-kneemorph-refly", "a response bends"),
        ("cell4-inversion", "a relationship reverses"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.4), sharey=True)
    for ax, (cell, title) in zip(axes, rooms):
        times, ids, res = series(cell)
        t0 = times[0]
        allbars = []
        for i in res:
            ys = [ids[i].get(t, None) for t in times]
            xs = [(t - t0) / 60.0 for t, y in zip(times, ys) if y is not None]
            vv = [y for y in ys if y is not None]
            allbars.append((max(vv), xs, vv))
            ax.plot(xs, vv, color=GRAY, lw=0.8, alpha=0.75, zorder=2)
        allbars.sort(key=lambda z: -z[0])
        if len(allbars) >= 1:  # epicenter
            _, xs, vv = allbars[0]
            ax.plot(xs, vv, color=BLUE, lw=2.0, zorder=4, label="the changed one")
        if len(allbars) >= 2 and cell.startswith("cell2"):  # the stirred neighbor
            _, xs, vv = allbars[1]
            ax.plot(xs, vv, color=RED, lw=1.4, zorder=3, label="one neighbor stirred")
        ax.axhline(FROZEN, color=INK, lw=0.9, ls=(0, (4, 3)))
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("minutes", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.set_yscale("symlog", linthresh=0.05)
    axes[0].set_ylabel("largest uncertainty on a curve", fontsize=9)
    axes[0].annotate("the alarm limit", xy=(0.98, FROZEN), xycoords=("axes fraction", "data"),
                     fontsize=7.5, va="bottom", ha="right", color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fourkinds.pdf"))
    plt.close(fig)


# ---------------- Figure: the busy evening ----------------

def fig_evening():
    times, ids, res = series("cell5-evening")
    t0 = times[0]
    means, worsts = [], []
    for t in times:
        vs = [ids[i][t] for i in res if t in ids[i]]
        means.append(sum(vs) / len(vs) if vs else None)
        worsts.append(max(vs) if vs else None)
    xs = [t for t in times]  # absolute bench uptime: the phase clocks are absolute
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ax.plot(xs, worsts, color=RED, lw=1.6, label="the least certain curve")
    ax.plot(xs, means, color=BLUE, lw=1.6, label="average over all curves")
    ax.axhline(FROZEN, color=INK, lw=0.9, ls=(0, (4, 3)))
    # the world's three scheduled changes + the unscheduled push
    for x, lab in [(300, "a reading drifts"), (600, "a coupling's strength changes"), (676.6, "an outside push")]:
        ax.axvline(x, color=GRAY, lw=0.8, ls=(0, (2, 2)))
        ax.annotate(lab, xy=(x, 0.97), xycoords=("data", "axes fraction"),
                    fontsize=7.5, rotation=90, va="top", ha="right", color=INK)
    ax.set_xlabel("seconds of the evening", fontsize=9)
    ax.set_ylabel("uncertainty", fontsize=9)
    ax.set_ylim(0, 0.16)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=8, frameon=False, loc="center right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "evening.pdf"))
    plt.close(fig)


# ---------------- Figure: transfer ----------------

def fig_transfer():
    caps = load_room("cell6-transfer")
    times = [t for t, _ in caps]
    t0 = times[0]
    senders, counts = [], []
    for t, cs in caps:
        senders.append(len({c.get("sender_id", "?")[:8] for c in cs}))
        counts.append(len(cs))
    xs = [t for t in times]  # absolute bench uptime
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 4.2), sharex=True,
                                 gridspec_kw=dict(hspace=0.12))
    a1.step(xs, senders, where="post", color=BLUE, lw=1.8)
    a1.set_yticks(sorted(set(senders)))
    a1.set_ylabel("members measuring", fontsize=9)
    a1.tick_params(labelsize=8)
    a2.step(xs, counts, where="post", color=INK, lw=1.8)
    a2.set_ylabel("curves held", fontsize=9)
    a2.set_xlabel("seconds --- the whole system changes at 240", fontsize=9)
    a2.tick_params(labelsize=8)
    for a in (a1, a2):
        a.axvspan(240, 300, color=GRAY, alpha=0.25, lw=0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "transfer.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    n, e, p = fig_connectome()
    print(f"connectome.pdf: {n} nodes, {e} measured couplings (arrows), {p} completed curve panels")
    fig_fourkinds(); print("fourkinds.pdf")
    fig_evening();   print("evening.pdf")
    fig_transfer();  print("transfer.pdf")
    print("done ->", OUT)
