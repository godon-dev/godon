#!/usr/bin/env python3
"""The two change tests on the quiet chain bench.

Chain: node-1 --0.7--> node-3 --0.5--> node-2, saturation carriers,
hold position 50 (all params), carriers = param_1, dead = param_0/2.

Curves from the completed walk (/tmp/chain_curves.json):
  A=node-1, C=node-3, B=node-2 (objective_0 = the coupled channel)

Attempt 1 — hold-out prediction: set A's param_1 to unvisited levels
(56, 68), compare B's settled objective_0 against the INTERPOLATED
composed prediction (committed before measuring, printed from curves).

Attempt 2 — steering precursor: pick target r* for B on the tent's
rising flank, invert the composed map to get A's level, execute,
measure the landing.

Bench protocol (from sim.rs): POST /node-N/apply sets params and runs
the full relaxation SYNCHRONOUSLY; each read (apply response or
GET /node-N/metrics/json) draws fresh noise sigma=0.02 per objective.
Settle = immediate. Sample N times, median + MAD.

Usage: on runner: python3 gate_change_tests.py
"""
import json
import math
import statistics
import urllib.request

BASE = "http://127.0.0.1:8095"
HOLD = {"param_0": 50.0, "param_1": 50.0, "param_2": 50.0}
CURVES = json.load(open("/tmp/chain_curves.json"))

def apply(node, params):
    payload = json.dumps(params).encode()
    req = urllib.request.Request(
        f"{BASE}/{node}/apply", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def read(node):
    with urllib.request.urlopen(f"{BASE}/{node}/metrics/json", timeout=10) as r:
        return json.loads(r.read())

def get_curve(sender, recv):
    for c in CURVES:
        if (c["sender_id"].startswith(sender) and c["receiver_id"].startswith(recv)
                and c["param"] == "param_1" and c["channel"] == "objective_0"):
            pts = sorted(c["state"]["points"])
            return [(p[0], p[1], p[2]) for p in pts]
    raise SystemExit(f"curve {sender}->{recv} not found")

def interp(points, x):
    """Linear interpolation on (level, response, bar); clamped at ends."""
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for (x0, y0, _), (x1, y1, _) in zip(points, points[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    raise ValueError(x)

def settle_sample(node, n=15):
    """Hold everything still; sample node's objective_0 n times."""
    vals = [read(node)["objective_0"] for _ in range(n)]
    return statistics.median(vals), 1.4826 * statistics.median(
        [abs(v - statistics.median(vals)) for v in vals])

# ── Setup: park every node at hold ─────────────────────────────────
for n in ("node-1", "node-2", "node-3"):
    apply(n, HOLD)
print("all nodes parked at hold (50,50,50)")

c_AC = get_curve("42646858", "3a9d648e")   # A -> C one hop
c_AB = get_curve("42646858", "51c38a1d")   # A -> B two hop

# baseline: B's settled objective at all-hold
base_med, base_mad = settle_sample("node-2")
print(f"B baseline settled objective_0 = {base_med:+.4f} (mad {base_mad:.4f})")

# sanity anchor: A at level 100 via direct API vs walk-measured shift
r = apply("node-1", dict(HOLD, param_1=100.0))
vals = [read("node-2")["objective_0"] for _ in range(15)]
med = statistics.median(vals)
shift = med - base_med
print(f"sanity: A@param_1=100 -> B shift {shift:+.4f} "
      f"(walk curve said -0.0522, identity pred -0.0504)")

# ── Attempt 1: hold-out prediction at unvisited levels ─────────────
print("\n=== ATTEMPT 1: HOLD-OUT PREDICTION (levels 56, 68) ===")
for L in (56.0, 68.0):
    pred_one_hop = interp(c_AC, L)
    pred = 0.5 * pred_one_hop
    print(f"\nL={L}: committed prediction (0.5 x interp A->C({L}) = "
          f"{pred_one_hop:+.4f}) -> B shift {pred:+.4f}")
    apply("node-1", dict(HOLD, param_1=L))
    med, mad = settle_sample("node-2")
    meas = med - base_med
    bar = math.sqrt(mad * mad + base_mad * base_mad) or 0.02
    sig = abs(meas - pred) / bar
    print(f"  measured shift {meas:+.4f} +/- {bar:.4f}  "
          f"dev {meas - pred:+.4f} = {sig:.2f} sigma  "
          f"{'HOLDS' if sig <= 2.0 else 'DEVIATES'}")
    apply("node-1", HOLD)

# ── Attempt 2: steering precursor ──────────────────────────────────
print("\n=== ATTEMPT 2: STEERING PRECURSOR ===")
# composed forward map: f(L) = 0.5 * interp(c_AC, L) (B shift).
# Target on the steep LEFT flank (between levels 0 and 38), where the
# map is monotone and invertible: r* = -0.10.
r_star = -0.10
def composed(L):
    return 0.5 * interp(c_AC, L)
# invert by bisection on [0, 50] (monotone rising branch)
lo, hi = 0.0, 50.0
for _ in range(60):
    mid = (lo + hi) / 2
    if composed(mid) < r_star:
        lo = mid
    else:
        hi = mid
L_star = (lo + hi) / 2
print(f"target r* = {r_star:+.4f}  ->  map-derived A level = {L_star:.2f}")
print(f"(check: composed({L_star:.2f}) = {composed(L_star):+.4f})")

apply("node-1", dict(HOLD, param_1=L_star))
med, mad = settle_sample("node-2")
landed = med - base_med
bar = math.sqrt(mad * mad + base_mad * base_mad) or 0.02
sig = abs(landed - r_star) / bar
print(f"executed A={L_star:.2f}; B landed at {landed:+.4f} +/- {bar:.4f}")
print(f"target {r_star:+.4f}  dev {landed - r_star:+.4f} = {sig:.2f} sigma  "
      f"{'LANDED' if sig <= 2.0 else 'MISSED'}")
apply("node-1", HOLD)
print("\ndone; A returned to hold.")
