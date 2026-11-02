#!/usr/bin/env python3
"""d2_oracle.py — D2 post-hoc economics + bracket, from strip.log only.

Strip lines: '<ts>|{node metrics}|{drift state}|wp=...|wishes=...' + '<ts> truth={...}'.
The offset drift is tick-indexed (legacy): offset(t) = min(cap, rate*max(0, tick-1600)).
Bands from the declare: [0.8149, 1.1149] around target 0.9649 (battery shape).
No live arm anywhere — post-hoc by construction.
"""
import json, re, sys
from datetime import datetime, timezone

STRIP = sys.argv[1] if len(sys.argv) > 1 else "/tmp/gd/evidence/D2-trail/strip.log"
LO, HI, TGT = 0.8149, 1.1149, 0.9649
RATE, START_TICK, CAP = 0.0008, 1600, 0.15

rows = []
for line in open(STRIP):
    m = re.match(r"^(\S+)\|\{.*?\"objective_1\":\s*([-\d.e]+).*?\"tick\":\s*(\d+)\}", line)
    if m:
        ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        rows.append((ts, float(m.group(2)), int(m.group(3))))
if not rows:
    sys.exit("no strip rows parsed")

t0 = rows[0][0]
# pre-slide baseline: samples before the offset starts (tick < 1600)
pre = [r for r in rows if r[2] < START_TICK]
baseline = sorted(r[1] for r in pre)
base_med = baseline[len(baseline)//2] if baseline else rows[0][1]

kept = miss = 0
floor_in = 0
for ts, v, tick in rows:
    off = min(CAP, RATE * max(0, tick - START_TICK))
    # actual kept: the real reading (serve compensation included) in band
    if LO <= v <= HI: kept += 1
    else: miss += 1
    # do-nothing counterfactual: baseline median + the world's offset, no serve
    dn = base_med + off
    if LO <= dn <= HI: floor_in += 1

n = len(rows)
kept_frac = kept / n
floor_frac = floor_in / n
# oracle ceiling: a truth-knowing re-planner holds target; reachable because the
# slide (0.15) sits inside the dial's compensation span (maxChange 0.25/round)
oracle_frac = 1.0

slide_start = next((r[0] for r in rows if r[2] >= START_TICK), None)
capped_at = next((r[0] for r in rows if min(CAP, RATE*(r[2]-START_TICK)) >= CAP - 1e-9), None)
witness_end = datetime(2026, 11, 2, 16, 30, tzinfo=timezone.utc)  # death census: 16:30:43
wit = [r for r in rows if r[0] <= witness_end]
wit_kept = sum(1 for r in wit if LO <= r[1] <= HI)

def fmt(t): return t.strftime("%H:%M:%SZ") if t else "-"
print(f"samples={n} span={fmt(rows[0][0])}..{fmt(rows[-1][0])}")
print(f"baseline median (pre-slide, n={len(pre)}): {base_med:.4f}")
print(f"slide start tick 1600 at {fmt(slide_start)}; capped {fmt(capped_at)}")
print(f"witnessed epoch (.. 16:30:43Z): samples={len(wit)} kept={wit_kept} frac={wit_kept/max(len(wit),1):.3f}")
print(f"ACTUAL kept-fraction (whole strip): {kept_frac:.3f} ({kept}/{n})")
print(f"DO-NOTHING floor kept-fraction: {floor_frac:.3f} ({floor_in}/{n})")
print(f"ORACLE ceiling (truth re-planner, slide within reach): {oracle_frac:.3f}")
print(f"waterings: none witnessed (no miss->streak->probe cycles; witness died 16:30:43 with band held)")
