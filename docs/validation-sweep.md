# Validation Sweep Strategy

## Status

- **DONE**: Linear chain4 (0.7 → 0.5 → 0.3) — 3 edges detected, measured values match planted coupling × 0.5
- **NEXT**: Systematic sweep across coupling shapes, noise levels, and topologies

## Experimental Dimensions

### 1. Coupling Shape (base_function parameter)

| Shape        | Description                          | Expected Detection Behavior                          | Status   |
|--------------|--------------------------------------|------------------------------------------------------|----------|
| linear       | `objective = w·params`               | Step change = strength × 0.5. CFAR works.            | DONE     |
| threshold    | `objective = 0 if params < T else w` | Discontinuous step. CFAR should detect if T crossed. | PENDING  |
| saturation   | `objective = w·tanh(params)`         | Flattens at extremes. Push amplitude may be limited. | PENDING  |
| polynomial   | `objective = w·params²`              | Nonlinear response. Step change depends on base pt. | PENDING  |
| sigmoid      | `objective = w·sigmoid(params)`      | S-curve. Detection depends on operating point.      | PENDING  |

**Key question**: At what coupling nonlinearity does the CFAR step-change detector fail? Do we need a different detector for nonlinear coupling?

**Config**: pair topology (2 nodes, 1 edge), coupling=0.7, noise=0.02, sweep base_function.

### 2. Noise Robustness

| Gaussian σ | Colored σ | Expected Behavior                                    | Status  |
|------------|-----------|------------------------------------------------------|---------|
| 0.01       | 0.0       | Near-noiseless. All edges trivially detectable.      | PENDING |
| 0.02       | 0.0       | Current baseline. Proven on chain4.                  | DONE    |
| 0.05       | 0.0       | Moderate noise. Weak edges (0.3) may fail.           | PENDING |
| 0.10       | 0.0       | High noise. Only strong edges (0.7) likely survive.  | PENDING |
| 0.20       | 0.0       | Extreme noise. Detection boundary.                   | PENDING |
| 0.02       | 0.05      | Colored noise. Baseline drift.                       | PENDING |
| 0.02       | 0.10      | Strong colored noise. False positives risk.          | PENDING |

**Key question**: What is the minimum detectable coupling strength at each noise level? This gives the detection sensitivity curve (effective ROC).

**Config**: pair topology, base=linear, sweep noise_gaussian and noise_colored.

### 3. Topology

| Topology          | Nodes | Edges | Description                                   | Status  |
|-------------------|-------|-------|-----------------------------------------------|---------|
| Pair              | 2     | 1     | Simplest case. Single edge detection.         | DONE    |
| Chain4            | 4     | 3     | Linear chain. Composition validation.         | DONE    |
| Chain6            | 6     | 5     | Longer chain. Does composition hold at depth? | PENDING |
| Diamond           | 4     | 5     | A→B, A→C, B→D, C→D, B→C. Branching + merge.  | PENDING |
| Triangle          | 3     | 3     | A↔B, B↔C, A↔C. Bidirectional coupling.        | PENDING |
| Star              | 5     | 4     | Center node → 4 leaves. One-to-many.          | PENDING |

**Key question**: Does the scanner recover the correct edge set for non-chain topologies? Does composition predict distant-node response through branching paths?

**Config**: varies per topology. All at coupling=0.5, base=linear, noise=0.02.

### 4. Coupling Strength Sweep

| Strength | Expected rising_edge (×0.5) | Detection Confidence | Status  |
|----------|-----------------------------|----------------------|---------|
| 0.1      | 0.05                        | Likely below CFAR    | PENDING |
| 0.2      | 0.10                        | Borderline           | PENDING |
| 0.3      | 0.15                        | Detectable (chain4)  | DONE    |
| 0.5      | 0.25                        | Detectable (chain4)  | DONE    |
| 0.7      | 0.35                        | Strong (chain4)      | DONE    |
| 0.9      | 0.45                        | Very strong          | PENDING |

**Key question**: What is the minimum coupling strength detectable at noise=0.02?

**Config**: pair topology, base=linear, noise=0.02, sweep coupling_strength.

## Priority Order for Paper

1. **Linear pair sweep** (coupling strength + noise) — defines detection sensitivity curve
2. **Diamond topology** — proves non-chain generalization with branching + composition
3. **One nonlinear shape** (threshold or saturation) — shows boundary of method
4. **Chain4 repeated at higher noise** — shows degradation gracefully

Items 1-2 are the paper's experimental core. Item 3 prevents "it only works on linear" critique. Item 4 is a robustness bonus.

## Topology Files Needed

```
examples/bench/
  scenario-generic-pair/          # EXISTS — 2 nodes, 1 edge
  scenario-generic-chain4/        # EXISTS — 4 nodes, 3 edges
  scenario-generic-chain6/        # NEEDED — 6 nodes, 5 edges
  scenario-generic-diamond/       # NEEDED — 4 nodes, 5 edges (A→B,A→C,B→D,C→D,B→C)
  scenario-generic-triangle/      # NEEDED — 3 nodes, 3 bidirectional edges
  scenario-generic-star/          # NEEDED — 5 nodes, center → 4 leaves
```

## Workflow Files Needed

```
.github/workflows/
  bench-generic.yml               # EXISTS — pair
  bench-chain4.yml                # EXISTS — chain4
  bench-diamond.yml               # NEEDED
  bench-triangle.yml              # NEEDED
```

## Per-Run Protocol

For each scenario:
1. Run bench workflow (min_trials=200)
2. While breeders still active: call `/detect/{sender}/{receiver}` per pair
3. Record: detected, confidence, rising_edge, baseline_mad, rounds_detected/rounds_total
4. Compare measured rising_edge against expected (shape-dependent)
5. Check false positive rate across non-edge pairs

## Expected vs Measured

For linear coupling: `expected_rising = strength × (max_base - neutral_base) = strength × 0.5`

For nonlinear: expected depends on the response function evaluated at push vs neutral params.
The bench computes this internally — we compare against the bench's `/config` endpoint output.

## Definition of Done

The paper's experimental section requires:
- [x] Chain4 composition validated (3 edges, correct strengths)
- [ ] Detection sensitivity curve (strength × noise grid on pair)
- [ ] Non-chain topology (diamond: correct edges + no false positives)
- [ ] One nonlinear coupling shape characterized
- [ ] Composition prediction: do chained edges predict distant-node response?
