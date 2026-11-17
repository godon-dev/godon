#!/usr/bin/env python3
"""gen_topology.py — N-node DAG topologies for the generic bench (the N-ladder on generic).

Dependency-free on purpose (string-templated yaml — no pyyaml on the runner).

Families (all DAG by construction — cycles are a separate subject, never planted here):
  mesh  — upper-triangular complete DAG: every node influences every later node.
           The generic-bench equivalent of "fully coupled": node_1 drives all,
           node_N is driven by all. Comparable to the old microgrid receipts.
  chain — node_i -> node_{i+1}: the sparse extreme; peer motion is local.
  fork  — node_1 -> every other node: one hub, many receivers; the receivers'
           readings all move when the hub walks (maximal shared-cause motion).

Every node: dials_per_node dials, 1 objective, linear base, weights 1.0 per dial.
Edges: one channel per edge (to_channel 0), strength from --coupling, no drift.
"""
import argparse

p = argparse.ArgumentParser()
p.add_argument("--n", type=int, required=True)
p.add_argument("--family", choices=["mesh", "chain", "fork", "none"], default="mesh")
p.add_argument("--coupling", type=float, default=0.7)
p.add_argument("--dials", type=int, default=1)
p.add_argument("--sigma", type=float, default=0.02)
a = p.parse_args()

lines = ["nodes:"]
for i in range(1, a.n + 1):
    lines += [
        f"  - id: node-{i}",
        f"    params: {a.dials}",
        "    objectives: 1",
        "    base: linear",
        "    param_lower: 0.0",
        "    param_upper: 100.0",
        "    weights:",
    ]
    for _ in range(1):  # one objective row
        lines.append("      - [" + ", ".join("1.0" for _ in range(a.dials)) + "]")

edges = []
if a.family == "mesh":
    for i in range(1, a.n + 1):
        for j in range(i + 1, a.n + 1):
            edges.append((i, j))
elif a.family == "chain":
    for i in range(1, a.n):
        edges.append((i, i + 1))
elif a.family == "fork":
    for j in range(2, a.n + 1):
        edges.append((1, j))
# "none": zero edges — the uncoupled control column

if edges:
    lines.append("edges:")
    for i, j in edges:
        lines += [
            f"  - from: node-{i}",
            "    from_channel: 0",
            f"    to: node-{j}",
            "    to_channel: 0",
            f"    strength: {a.coupling}",
            "    drift_rate: 0.0",
        ]
else:
    lines.append("edges: []")
lines += [
    "noise:",
    f"  gaussian_sigma: {a.sigma}",
    "  colored_sigma: 0.0",
    "  drift_rate: 0.0",
]
print("\n".join(lines))
