import sys, json

data = json.load(sys.stdin)
port = sys.argv[1] if len(sys.argv) > 1 else "unknown"

factor = data.get("coupling_factor", 0)
neighbors = data.get("coupling_neighbors", [])

assert factor == 0 or factor is None, f"Port {port}: unexpected coupling factor={factor}"
assert len(neighbors) == 0, f"Port {port}: unexpected neighbors {neighbors}"
print(f"Port {port}: no coupling (OK)")
