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
    """Figure 1: LEFT the DAG (the room's whole measured wiring, plain
    arrows); RIGHT one small panel per measured edge — that edge's own
    response curve, every point with its bar, red dashed where the
    stretch is unmeasured (priced ignorance). All the per-edge detail,
    none of it overlapped."""
    caps = load_room("cell6-transfer")
    up, curves = max(caps, key=lambda x: len(x[1]))  # the fullest measured map

    nodes = []
    for c in curves:
        for r in (c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8]):
            if r not in nodes:
                nodes.append(r)
    letters = {n: chr(ord("A") + i) for i, n in enumerate(nodes)}
    senders = {c.get("sender_id", "?")[:8] for c in curves}
    receivers = {c.get("receiver_id", "?")[:8] for c in curves}

    # DAG columns: sources left, both middle, pure receivers right
    col = {}
    for n in nodes:
        s, r = n in senders, n in receivers
        col[n] = 0.0 if (s and not r) else (0.5 if (s and r) else 1.0)
    cols = {}
    for n in nodes:
        cols.setdefault(col[n], []).append(n)
    pos = {}
    for x, ns in cols.items():
        for i, n in enumerate(ns):
            pos[n] = (x, (i - (len(ns) - 1) / 2.0))

    n_edges = len(curves)
    ncols = 4 if n_edges > 8 else (3 if n_edges > 4 else 2)
    nrows = -(-n_edges // ncols)
    fig = plt.figure(figsize=(11.5, 1.9 + 1.9 * nrows))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 2.7], wspace=0.18)
    ax = fig.add_subplot(gs[0])
    gsr = gs[1].subgridspec(nrows, ncols, hspace=0.55, wspace=0.30)

    # LEFT: the DAG
    pairs = {(c.get("sender_id", "?")[:8], c.get("receiver_id", "?")[:8]) for c in curves}
    for s, r in pairs:
        if s == r:
            continue
        x1, y1 = pos[s]; x2, y2 = pos[r]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        ux, uy = dx / L, dy / L
        ax.annotate("", xy=(x2 - 0.16 * ux, y2 - 0.16 * uy),
                    xytext=(x1 + 0.16 * ux, y1 + 0.16 * uy),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2,
                                    shrinkA=0, shrinkB=0, alpha=0.85))
    for n, (x, y) in pos.items():
        ax.add_patch(plt.Circle((x, y), 0.14, fc="white", ec=INK, lw=1.4, zorder=6))
        ax.text(x, y, letters[n], ha="center", va="center", fontsize=11,
                fontweight="bold", color=INK, zorder=7)
    ax.set_xlim(-0.75, 1.75); ax.set_ylim(-2.6, 2.6)
    ax.set_aspect("equal"); ax.axis("off")

    # RIGHT: one small panel per edge — the curve's own measured points
    # (level, response, bar) from the store's `points`; red dashed over
    # the stretches no probe covered (unresolved gaps). The house rule:
    # points are the measurement; gaps are the priced ignorance between.
    for i, c in enumerate(curves):
        s = letters[c.get("sender_id", "?")[:8]]
        r = letters[c.get("receiver_id", "?")[:8]]
        a = fig.add_subplot(gsr[i])
        st = c.get("state", {})
        pts = sorted(st.get("points", []), key=lambda p: p[0])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        es = [abs(p[2]) for p in pts]
        if xs:
            a.vlines(xs, [y - e for y, e in zip(ys, es)],
                     [y + e for y, e in zip(ys, es)], color=BLUE, lw=0.8, zorder=3)
            a.plot(xs, ys, color=BLUE, lw=0.9, zorder=4)
            a.plot(xs, ys, "o", color=BLUE, ms=2.2, zorder=5)
            # red dashed across each unresolved stretch, at the interp level
            def interp(x):
                if x <= xs[0]: return ys[0]
                if x >= xs[-1]: return ys[-1]
                for j in range(1, len(xs)):
                    if xs[j] >= x:
                        f = (x - xs[j-1]) / max(1e-9, xs[j] - xs[j-1])
                        return ys[j-1] + f * (ys[j] - ys[j-1])
                return ys[-1]
            for g in st.get("gaps", []):
                if g.get("unresolved"):
                    a.plot([g["from_level"], g["to_level"]],
                           [interp(g["from_level"]), interp(g["to_level"])],
                           ls=(0, (3, 2)), lw=1.3, color=RED, zorder=6)
            a.set_xlim(-5, 105)
        a.set_title(f"{s} to {r}", fontsize=7.5, pad=3)
        a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_linewidth(0.6)

    fig.savefig(os.path.join(OUT, "connectome.pdf"), bbox_inches="tight")
    plt.close(fig)
    return len(nodes), n_edges


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
    axes[0].set_ylabel("worst bar on a curve", fontsize=9)
    axes[0].annotate("frozen bar", xy=(0.98, FROZEN), xycoords=("axes fraction", "data"),
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
    ax.plot(xs, worsts, color=RED, lw=1.6, label="worst relationship")
    ax.plot(xs, means, color=BLUE, lw=1.6, label="mean over all curves")
    ax.axhline(FROZEN, color=INK, lw=0.9, ls=(0, (4, 3)))
    # the world's three scheduled changes + the unscheduled push
    for x, lab in [(300, "a sensor slides"), (600, "a weight morphs"), (676.6, "an outside push")]:
        ax.axvline(x, color=GRAY, lw=0.8, ls=(0, (2, 2)))
        ax.annotate(lab, xy=(x, 0.97), xycoords=("data", "axes fraction"),
                    fontsize=7.5, rotation=90, va="top", ha="right", color=INK)
    ax.set_xlabel("seconds of the evening", fontsize=9)
    ax.set_ylabel("uncertainty bar", fontsize=9)
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
    a1.set_ylabel("probers", fontsize=9)
    a1.tick_params(labelsize=8)
    a2.step(xs, counts, where="post", color=INK, lw=1.8)
    a2.set_ylabel("curves held", fontsize=9)
    a2.set_xlabel("seconds (regime change at 240)", fontsize=9)
    a2.tick_params(labelsize=8)
    for a in (a1, a2):
        a.axvspan(240, 300, color=GRAY, alpha=0.25, lw=0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "transfer.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    n, e = fig_connectome()
    print(f"connectome.pdf: {n} nodes, {e} measured edges")
    fig_fourkinds(); print("fourkinds.pdf")
    fig_evening();   print("evening.pdf")
    fig_transfer();  print("transfer.pdf")
    print("done ->", OUT)
