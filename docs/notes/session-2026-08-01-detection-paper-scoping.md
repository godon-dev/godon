# Session 2026-08-01 — Detection Paper Scoping

## Paper Structure (3 papers, sequential)

- **Paper 1 — Detection**: The push/pause/hold protocol makes coupling detectable. CFAR is the detection backend (pluggable, not the contribution). Protocol is coupling-shape-agnostic (linear, threshold, saturation, polynomial — doesn't model the coupling function). Agents are autonomous optimizers, unaware of each other, communicating only through the shared substrate. The protocol coordinates them to take turns (one pushes, others hold) — scheduling constraint, not information exchange. Proven on greenhouse (coupling 0.9 bidirectional, 0.0 clean control) and bench-generic chain4 (3 edges, 0 false positives).
- **Paper 2 — Calibration of automatic characterization**: The sweep IS the paper. Sensitivity floor, noise robustness boundary, topology generalization, nonlinear coverage. Every grid cell is a calibration data point.
- **Paper 3 — Composition prediction + causal model**: Forward simulation to predict distant-node response. Future: agents cooperate once coupling understood.

## Framing Decisions

- No super-novelty claim. Present as "one method, measured boundaries." The related work section is context, not a wall. No exhaustive prior-art hunt.
- Components aren't new (CFAR is 1960s radar, ABA block design is classical, turn-taking is scheduling). Contribution is the specific assembly working as a deployable instrument with characterized limits.
- Coupling-shape-agnostic claim is central to Paper 1. Nonlinear coverage is not a side experiment — it's evidence for the core generality claim.

## Sweep Methodology Decisions

- The sweep IS characterization, not pass/fail. Report the boundary honestly. "At noise sigma 0.02, minimum detectable coupling is 0.2." That boundary IS the result.
- Do NOT tweak detector during sweep. An instrument paper where you iterate until it passes your own benchmark is not credible.
- Two failure types: (1) Expected degradation (weak coupling at high noise) — report it, that's the floor. (2) Unexpected failure (strong coupling at low noise) — debug, instrument is broken.
- No minimum performance bar to clear. Honest boundary is stronger than gamed pass rate. Greenhouse results already show real-system competence.

## Gaps Identified in Current Sweep Plan

1. **No systematic false positive characterization.** CFAR's central property is Constant False-Alarm Rate. That claim is empirically untested across conditions. Need genuinely uncoupled nodes (coupling=0.0) at each noise level to measure actual false alarm rate. Non-edge pairs in a connected topology are NOT true negatives (indirect coupling = composition question).
2. **No controlled passive-method comparison on synthetic data.** Greenhouse shows passive methods fail, but bench-generic gives exact ground truth with controllable noise. Running cross-correlation/Granger/TE on same trial data would convert "active works" from assertion to controlled experiment. (Optional — greenhouse already demonstrates this, but synthetic is cleaner for a reviewer.)

## Key Contribution Stack (Paper 1)

1. Autonomous optimizers with their own objectives, unaware of each other
2. Communication only through the shared substrate they are tending
3. Push/pause/hold protocol: coordinated active perturbation (ABA block design, turn-taking with fencing tokens)
4. CFAR detection: reversible step-change detector, coupling-shape-agnostic
5. Honest characterization: measured boundary of method competence

The protocol makes the signal. CFAR detects it. The novelty is the assembly, not any single component.
