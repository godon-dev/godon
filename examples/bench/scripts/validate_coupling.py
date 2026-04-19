import sys, json

data = json.load(sys.stdin)
port = sys.argv[1] if len(sys.argv) > 1 else "unknown"

factor = data.get("coupling_factor", 0)
neighbors = data.get("coupling_neighbors", [])

assert factor > 0, f"Port {port}: expected coupling_factor > 0, got {factor}"
assert len(neighbors) > 0, f"Port {port}: expected coupling neighbors, got {neighbors}"
print(f"Port {port}: coupling_factor={factor}, neighbors={neighbors} (OK)")
