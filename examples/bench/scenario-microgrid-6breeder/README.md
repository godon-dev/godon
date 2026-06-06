# Scenario: Microgrid 6-Breeder Topology Discovery

Scaled variant of the standard microgrid bench with 6 fully-coupled breeders. Tests pairwise interference detection at scale — 15 coupling pairs, maxing out the current prime-frequency watermark encoding (12 primes, 2 per breeder).

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
# Deploy 6 breeders against their respective microgrid targets
# Observer detects interference across all 15 pairs
```

## What It Validates

- Pairwise detection scales beyond 2 breeders
- Watermark encoding holds with 6 concurrent breeders
- Observer can handle multiple simultaneous detection streams
- Foundation for topology graph assembly from pairwise detections

## Constraints

- Uses all 12 available primes (2 per breeder) — maximum for current FDMA encoding
- Each breeder needs its own microgrid target instance
- Coupling factor configurable via `COUPLING_FACTOR` env var (default: 0.1)
