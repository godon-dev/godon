# Scenario: Microgrid 6-Systemtender Topology Discovery

Scaled variant of the standard microgrid bench with 6 fully-coupled systemtenders. Tests pairwise interference detection at scale — 15 coupling pairs, maxing out the current prime-frequency watermark encoding (12 primes, 2 per systemtender).

## Topology

Fully connected — each microgrid instance couples to all others:

```
    1 ─── 2
    │╲   ╱│
    │ ╲ ╱ │
    │  ╳  │
    │ ╱ ╲ │
    │╱   ╲│
    4 ─── 5
    │╲   ╱│
    │ ╲ ╱ │
    │  6  │
    └─────┘
```

## Running

```bash
docker compose up -d
# Deploy 6 systemtenders against their respective microgrid targets
# Observer detects interference across all 15 pairs
```

## What It Validates

- Pairwise detection scales beyond 2 systemtenders
- Watermark encoding holds with 6 concurrent systemtenders
- Observer can handle multiple simultaneous detection streams
- Foundation for topology graph assembly from pairwise detections

## Constraints

- Uses all 12 available primes (2 per systemtender) — maximum for current FDMA encoding
- Each systemtender needs its own microgrid target instance
- Coupling factor configurable via `COUPLING_FACTOR` env var (default: 0.1)
