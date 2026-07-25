# Generic Bench Scenarios

## Scenarios

| Scenario | Topology | Base | Noise |
|----------|----------|------|-------|
| scenario-generic-pair | 2 nodes, 1 edge (0.7) | linear | gaussian |
| scenario-generic-chain4 | 4 nodes chain (0.7/0.5/0.3) | linear | gaussian |
| scenario-generic-nonlinear | 2 nodes, 1 edge (0.7) | saturation | gaussian |
| scenario-generic-noisy | 2 nodes, 1 edge (0.7) | linear | gaussian+colored |

## Usage

```
cd scenario-generic-pair
docker compose up -d
```

The topology.yaml in each scenario is the ground truth. The bench exposes
`GET /config` which returns the same topology for verification.
