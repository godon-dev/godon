#!/usr/bin/env python3
import json, math
curves = json.load(open("/tmp/chain_curves.json"))
# A=node-1=42646858, C=node-3=3a9d648e, B=node-2=51c38a1d
def get(sender, recv, param, ch):
    for c in curves:
        if c["sender_id"].startswith(sender) and c["receiver_id"].startswith(recv) \
           and c["param"] == param and c["channel"] == ch:
            return {p[0]: (p[1], p[2]) for p in c["state"]["points"]}
    return None

c_AC = get("42646858", "3a9d648e", "param_1", "objective_0")
c_AB = get("42646858", "51c38a1d", "param_1", "objective_0")
c_CB = get("3a9d648e", "51c38a1d", "param_1", "objective_0")

print("=== curve A->C (one hop, planted 0.7 x tent) ===")
for L in sorted(c_AC): print(f"  L={L:6.1f} r={c_AC[L][0]:+.4f} +/-{c_AC[L][1]:.4f}")
print("=== curve A->B (two hop, planted 0.35 x tent) ===")
for L in sorted(c_AB): print(f"  L={L:6.1f} r={c_AB[L][0]:+.4f} +/-{c_AB[L][1]:.4f}")

print()
print("=== THE IDENTITY: measured A->B  vs  0.5 x measured A->C ===")
shared = sorted(set(c_AC) & set(c_AB))
n_ok = 0
for L in shared:
    rAC, bAC = c_AC[L]; rAB, bAB = c_AB[L]
    pred = 0.5 * rAC
    dev = rAB - pred
    bar = math.sqrt((0.5*bAC)**2 + bAB**2) or 0.02
    sig = abs(dev)/bar
    ok = sig <= 2.0
    n_ok += ok
    print(f"  L={L:6.1f}  meas={rAB:+.4f}  pred={pred:+.4f}  dev={dev:+.4f}  {sig:5.2f} sigma  {'ok' if ok else 'DEVIATES'}")
print(f"\n{n_ok}/{len(shared)} levels within 2 sigma")
if c_CB:
    print("\n=== C->B leg (planted 0.5 x tent) ===")
    for L in sorted(c_CB): print(f"  L={L:6.1f} r={c_CB[L][0]:+.4f} +/-{c_CB[L][1]:.4f}")

# blanks: everything else should be flat — spot check
print("\n=== blanks (spans) ===")
for c in curves:
    pts = c["state"]["points"]
    if not pts: continue
    resp = [p[1] for p in pts]
    span = max(resp) - min(resp)
    flag = " <== NON-FLAT" if span > 0.1 else ""
    print(f"s={c['sender_id'][:8]} r={c['receiver_id'][:8]} {c['param']}/{c['channel'][:11]} span={span:.3f}{flag}")
