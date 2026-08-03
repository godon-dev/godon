# Detection Paper — Experiment Summary

## Observation Parameters (constant across all cells)

| Parameter | Value |
|-----------|-------|
| push_block_size | 15 trials (default, also sweep at 30) |
| pause_block_size | 15 trials (default, also sweep at 30) |
| min_optimize_trials | 15 |
| cooldown_trials | 5 |
| hold_params | param_0=50, param_1=50, param_2=50 (midpoint) |
| impulse push target | upper_bound × scale (100 × 1.0 = 100) |
| CFAR Pfa | 0.05 (confidence 0.95) |
| min_ref_cells | 3 (baseline samples per round) |
| min_test_cells | 3 (push/pause samples per round) |
| Expected rising_edge formula | strength × 0.5 (linear, step from 50→100) |

Note: CFAR k-factor = N_ref × (Pfa^(-1/N_ref) - 1). Threshold = k × MAD.
With ~15-30 baseline samples, k ≈ 2.8-3.1. More samples → lower k → lower threshold.

## Spree 1: Linear Pair Detection Floor + Noise + Nonlinear

### Group A — Detection floor (linear, noise=0.02)

| Cell | Strength | Noise | Shape | Detected | Confidence | Rising Edge | Expected | Baseline MAD |
|------|----------|-------|-------|----------|------------|-------------|----------|--------------|
| 01   | 0.1      | 0.02  | linear | **false**    | **0.00**     | **0.045**   | 0.05     | **0.0188**   |
| 02   | 0.2      | 0.02  | linear | **true**     | **1.00**     | **0.1052**  | 0.10     | **0.0272**   |
| 03   | 0.3      | 0.02  | linear | **true**     | **1.00**      | **0.1437**  | 0.15     | **0.0169**   |
| 04   | 0.5      | 0.02  | linear | **true**     | **1.00**     | **0.2572**  | 0.25     | **0.0300**   |
| 05   | 0.7      | 0.02  | linear | **true**     | **0.33**     | **0.3681**  | 0.35     | **0.0159**   |
| 06   | 0.9      | 0.02  | linear | **true**     | **0.50**     | **0.4565**  | 0.45     | **0.0259**   |

### Group B — Noise robustness (linear, strength=0.5)

| Cell | Strength | Noise | Shape | Detected | Confidence | Rising Edge | Expected | Baseline MAD |
|------|----------|-------|-------|----------|------------|-------------|----------|--------------|
| 07   | 0.5      | 0.01  | linear | **true**     | **0.40**     | **0.2373**  | 0.25     | **0.0343**   |
| 08   | 0.5      | 0.05  | linear | **true**     | **0.50**     | **0.2588**  | 0.25     | **0.0606**   |
| 09   | 0.5      | 0.10  | linear | **false**    | **0.00**     | **0.0000**  | 0.25     | **0.1242**   |
| 09b  | 0.5      | 0.10  | linear, block=30 | **false** | **0.00** | **0.0000** | 0.25 | **0.0931** |
| 10   | 0.5      | 0.20  | linear | **false**    | **0.00**     | **0.0000**  | 0.25     | **0.2534**   |

### Group C — False positives (linear, strength=0.0)

| Cell | Strength | Noise | Shape | Detected | Confidence | Rising Edge | Expected | Baseline MAD |
|------|----------|-------|-------|----------|------------|-------------|----------|--------------|
| 11   | 0.0      | 0.02  | linear | **false**    | **0.00**     | **0.0000**  | 0.00     | **0.0166**   |
| 12   | 0.0      | 0.10  | linear | **false**    | **0.00**     | **0.0000**  | 0.00     | **0.1159**   |

### Group D — Nonlinear generality (strength=0.7, noise=0.02)

| Cell | Strength | Noise | Shape      | Detected | Confidence | Rising Edge | Expected | Baseline MAD |
|------|----------|-------|------------|----------|------------|-------------|----------|--------------|
| 13   | 0.7      | 0.02  | saturation | **true**  | **0.67**     | **-0.1130** | TBD      | **0.0277**   |
| 14   | 0.7      | 0.02  | threshold  | **true**  | **0.33**     | **0.7030**  | TBD      | **0.0258**   |
| 15   | 0.7      | 0.02  | polynomial | **true**  | **1.00**     | **0.5172**  | TBD      | **0.0275**   |
| 16   | 0.3      | 0.02  | saturation | **false** | **0.00**     | **0.0000**  | TBD      | **0.0227**   |
| 17   | 0.3      | 0.02  | threshold  | **true**  | **0.67**     | **0.3112**  | TBD      | **0.0169**   |
| 18   | 0.3      | 0.02  | polynomial | **false** | **0.00**     | **0.0000**  | TBD      | **0.0052**   |

### Group Cb — Additional false positive (extreme noise)

| Cell | Strength | Noise | Shape | Detected | Confidence | Rising Edge | Expected | Baseline MAD |
|------|----------|-------|-------|----------|------------|-------------|----------|--------------|
| 19   | 0.0      | 0.20  | linear | **false**    | **0.00**     | **0.0000**  | 0.00     | **0.1358**   |

## Per-cell data

Each cell writes to: `experiments/cell-XX-{shape}-{strength}-{noise}/`
- `detect.json` — /detect output
- `trials.json` — /trials for both breeders
