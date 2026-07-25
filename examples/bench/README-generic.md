# Generic Bench Scenarios

Synthetic coupling validation with known ground truth.

The topology.yaml in each scenario IS the answer key. After detection
rounds complete, compare detected edges to the planted coupling.

## Scenarios

| Scenario | Topology | Purpose |
|----------|----------|---------|
| scenario-generic-pair | 2 nodes, linear, 0.7 coupling | Basic detection validation |
| scenario-generic-chain4 | 4 nodes chain, 0.7/0.5/0.3 | Composition test (keystone) |
| scenario-generic-nonlinear | 2 nodes, saturation base | Non-linearity effects on detection |
| scenario-generic-noisy | 2 nodes, gaussian+colored noise | Noise floor for detection |

## Usage

```
cd scenario-generic-pair
docker compose up -d

# Create targets
# Create breeders via godon-api

# After detection rounds complete:
# Compare detected edges from godon-causal /detect to topology.yaml
```

## Verification

The bench exposes `GET /config` which returns the full topology —
the planted coupling strengths. Compare these to the scanner's output.

For the chain4 composition test:
- Ground truth: 0.7 × 0.5 × 0.3 = 0.105
- Scanner measures each edge independently
- Forward simulation predicts the chain response
- Compare prediction to ground truth
