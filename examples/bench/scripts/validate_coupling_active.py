import sys

port = sys.argv[1] if len(sys.argv) > 1 else "unknown"

lines = [l for l in sys.stdin if "greenhouse_coupling_delta" in l and not l.startswith("#")]
assert len(lines) > 0, f"Port {port}: no coupling_delta metrics found"

non_zero = 0
for l in lines:
    val = float(l.split()[-1])
    if val != 0.0:
        non_zero += 1

print(f"Port {port}: {non_zero}/{len(lines)} coupling deltas non-zero")
assert non_zero > 0, f"Port {port}: all coupling deltas are zero - coupling not active!"
