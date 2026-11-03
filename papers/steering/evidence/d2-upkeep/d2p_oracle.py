#!/usr/bin/env python3
"""d2p_oracle.py — D2' post-hoc economics from strip.log (the card was evicted;
the strip's per-90s wish-state polls are the verdict timeline).

Band: hw 0.08 around 0.7335 -> [0.6535, 0.8135]. Drift: 0.0008/tick from 1600, cap 0.15.
"""
import re, sys
from datetime import datetime, timezone

STRIP = sys.argv[1] if len(sys.argv) > 1 else "/tmp/gd/evidence/D2prime-trail/strip.log"
LO, HI = 0.6535, 0.8135
RATE, START_TICK, CAP = 0.0008, 1600, 0.15

rows, states = [], []
for line in open(STRIP):
    m = re.match(r"^(\S+)\|\{.*?\"objective_1\":\s*([-\d.e]+).*?\"tick\":\s*(\d+)\}", line)
    if m:
        ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        rows.append((ts, float(m.group(2)), int(m.group(3))))
    ms = re.search(r"wishes=eb7ca8df:(\w+)", line)
    if ms:
        tsm = re.match(r"^([^|]+)", line)
        ts = datetime.strptime(tsm.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        states.append((ts, ms.group(1)))

live = [r for r in rows if r[2] > 0]  # bench-alive samples
print(f"strip samples: {len(rows)} (bench-alive: {len(live)})")
if live:
    print(f"span: {live[0][0]} .. {live[-1][0]}")
    pre = [r for r in live if r[2] < START_TICK]
    base_med = sorted(r[1] for r in pre)[len(pre)//2] if pre else live[0][1]
    print(f"pre-slide baseline median (n={len(pre)}): {base_med:.4f}")
    slide_start = next((r[0] for r in live if r[2] >= START_TICK), None)
    capped = next((r[0] for r in live if RATE*(r[2]-START_TICK) >= CAP - 1e-9), None)
    print(f"slide start: {slide_start} | capped: {capped}")
    kept = sum(1 for r in live if LO <= r[1] <= HI)
    floor_in = sum(1 for r in live if LO <= base_med + min(CAP, RATE*max(0, r[2]-START_TICK)) <= HI)
    n = len(live)
    print(f"ACTUAL kept-fraction: {kept/n:.3f} ({kept}/{n})")
    print(f"DO-NOTHING floor: {floor_in/n:.3f} ({floor_in}/{n})")
    print(f"ORACLE ceiling: 1.000 (slide 0.15 within dial reach)")
    # break episodes: consecutive out-of-band stretches
    episodes, in_break = [], False
    for ts, v, tick in live:
        out = not (LO <= v <= HI)
        if out and not in_break: in_break, e0 = True, ts
        if not out and in_break: in_break = False; episodes.append((e0, ts))
    if in_break: episodes.append((e0, live[-1][0]))
    print(f"band-break episodes (reading outside band): {len(episodes)}")
    for a, b in episodes[:8]:
        print(f"  {a.strftime('%H:%M')} -> {b.strftime('%H:%M')} ({(b-a).seconds//60} min)")
# wish-state change points
if states:
    print("wish state timeline (changes):")
    prev = None
    for ts, s in states:
        if s != prev:
            print(f"  {ts.strftime('%H:%M:%S')} {prev or '-'} -> {s}")
            prev = s
    # watering count: landed->missed transitions recovered back to landed
    seq = [s for _, s in states]
    waterings = sum(1 for i in range(1, len(seq)) if seq[i] == 'missed' and seq[i-1] in ('landed', 'undecidable'))
    reclaims = sum(1 for i in range(1, len(seq)) if seq[i] in ('landed', 'undecidable') and seq[i-1] == 'missed')
    print(f"miss onsets: {waterings} | recoveries: {reclaims}")
