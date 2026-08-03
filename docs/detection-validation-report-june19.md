# Detection Validation Report — June 19, 2026

## Executive Summary

Block design detection (push/pause with edge detection) was deployed and tested
against both coupled (0.9) and uncoupled (0.0) greenhouse benchmarks. The
architecture is validated but the detection still produces false positives
from temporal drift on energy and water objectives. Growth_rate (obj0) is
the only coupling-sensitive objective.

## Results Summary

| Direction | Coupling | Detected | Real? |
|-----------|----------|----------|-------|
| B1->B2 obj0 (growth) | 0.9 | True* | Ambiguous (MAD=0) |
| B1->B2 obj1 (energy) | 0.9 | True | FALSE — temporal drift |
| B1->B2 obj2 (water) | 0.9 | True | FALSE — temporal drift |
| B2->B1 obj0 (growth) | 0.9 | False | Correct (insufficient data) |
| B2->B1 obj1 (energy) | 0.9 | True | FALSE — temporal drift |
| B1->B2 obj0 (growth) | 0.0 | False | CORRECT — no false positive |
| B1->B2 obj1 (energy) | 0.0 | True | FALSE — temporal drift on uncoupled! |
| B1->B2 obj2 (water) | 0.0 | True | FALSE — temporal drift on uncoupled! |
| B2->B1 all | 0.0 | False | CORRECT — no false positives |

*obj0 coupled detection had MAD=0.0 (3 samples), SNR=37616 — unreliable numbers

## Key Findings

### 1. Growth_rate (obj0) is the ONLY reliable coupling indicator

- Coupled 0.9: rising_edge=-0.038 (shift detected, direction unclear)
- Uncoupled 0.0: rising_edge=0.066, SNR=0.40 — below threshold, NOT detected
- Growth_rate correctly separates coupled from uncoupled

### 2. Energy (obj1) and Water (obj2) produce FALSE POSITIVES on uncoupled data

- Uncoupled obj1: rising_edge=224, SNR=6.3 — detected with NO coupling
- Uncoupled obj2: rising_edge=70, SNR=10.1 — detected with NO coupling
- These metrics increase monotonically over time (temporal drift), not from coupling
- The block step detector sees the temporal trend as a "step"

### 3. Pause block capture is broken

- `pause_samples=1` or `pause_samples=0` in most cases
- Receiver trials during the pause block aren't being captured
- Timestamp alignment between sender pause boundaries and receiver trials is off
- This makes falling_edge unreliable (pause_median defaults to baseline_median)

### 4. MAD floor needed

- With 3 baseline samples, MAD=0.0 → SNR in the billions
- Need minimum 10 baseline samples and MAD floor of 0.01

## What Works

- Block design coordinator: push×15, pause×15 cycles complete correctly
- DB-backed phase counting: handles parallel workers
- Turn-taking: both breeders become sender with fair circulation
- Unique partial index: prevents parallel sends
- Growth_rate correctly shows NO false positive on uncoupled data

## What Needs Fixing

### Priority 1: Filter objectives
Only run detection on growth_rate (or coupling-sensitive objectives).
Energy and water are cumulative/simulated drift — always produce false positives.

### Priority 2: Fix pause block capture
The pause window timestamp alignment captures almost no receiver trials.
The propagation_lag (20s) and window boundaries need adjustment.

### Priority 3: MAD floor
Minimum MAD of 0.01 and minimum 10 baseline samples.

### Priority 4: Warmup timing
Async warmup interrupt causes inconsistent early trial patterns.

## Technical Details

### Deployed Versions
- Breeder: 0.109.0 (block design + DB-backed phase counting)
- Observer: 0.57.0 (block step detection with median/MAD)

### Block Design
- Sender: 15 trials of extreme params (push), then 15 trials of baseline params (pause)
- Receiver: holds throughout sender's entire round
- Detection: median comparison across baseline/push/pause windows with MAD noise

### Analogous Real-World Methods
- Geothermal TRT: inject heat, measure temperature step
- Groundwater tracer: inject dye, measure breakthrough curve
- EIT: inject current, measure voltage difference
All use sustained perturbation in diffusive media. None use rapid alternation.
