# Characterization Evidence — Engine Validation (August 2026)

Data owner for the engine-validation phase of Paper 2 ("Calibration of
automatic characterization"). Every row below is extracted from bench
runs on the godon stack; raw exports live in this directory. Engine:
breeder 0.154.0, causal 0.15.0, controller 0.54.0, bench-generic 0.2.1.

Scenario throughout (unless noted): 2 breeders, node-1 → node-2 edge
(strength 0.7, feeds channel 0 only), saturation base on param_1
(carrier weight 1.0), params 0/2 dead on channel 0, receiver returns
two objectives. Ground truth: response(L) = 0.7·(tent(L/100) − tent(0.5)),
tent(x) = x/(1+4|x−0.5|). Expected channel-1 response: zero everywhere.

## The instrument under test

Coverage walk (farthest-point, listening from trial 1), uncertainty-aware
curves (inverse-variance blending, MAD bars), z-scoring, drift flags,
priced termination (two-key retirement: converged AND every unresolved
gap priced below the local bar; ignorance = jump × width / range).

## Run 24 — calibration + one-way edge (first clean-stack run)

- Carrier level 100: −0.118 ± 0.022 vs truth −0.117 (0.05σ). Level 50
  flat (reference). Reverse direction (no edge): all 6 probe points flat
  within 1σ. Dead params retired at 3 probes ×2 directions.
- Stack: bench live-reads fix (0.2.1) deployed mid-session; this run
  validated it against planted truth.

## Run 25 — full-amplitude tent, 4/6 levels

- Level 0: −0.352 ± 0.020 vs −0.350 (0.09σ). Levels 50/75/100 all
  within 0.66σ. Walk truncated by trial-count gate at 4 levels — the
  gate, not physics (motivated the priced stop's two-key retirement).
- Gap analysis on the final curve introduced the priced-ignorance
  arithmetic later shipped as causal's gaps fact.

## Run 26 — priced stop validated live (first firing)

- Carrier walked 9 levels (deepest to date), every point ≤ 0.55σ:
  0/13/25/38/50/62/75/87/100 → −0.356/−0.312/−0.268/−0.160/+0.006/
  −0.055/−0.082/−0.103/−0.113 vs truth −0.350/−0.313/−0.262/−0.170/
  0.000/−0.057/−0.088/−0.104/−0.117.
- Retirement BY PRICE: converged (delta 0.0003) with 3 shape-honest
  unresolved gaps on the steep flank (ignorance 0.014/0.020/0.007, all
  ≤ local bar ~0.02). Refinement midpoints (13/38/62/87) funded by the
  price, not by schedule.

## Run 29 — multi-channel verdict (first two-channel run)

- Rows carried both objectives (write chain: recon → worker → shared
  table — three fixes, one per layer, each found by a live check).
- Channel 0: carrier tent reproduced (7 levels, ≤ 0.49σ on shown points).
- Channel 1: ALL 8 curves (2 senders × params × channels where present)
  flat — max deviation 0.73σ. The carrier's tent is invisible on channel
  1 exactly as planted. First demonstration that param→channel influence
  is measured, not assumed: param_1 influences objective_0 (7-level
  structure) and not objective_1 (7 levels of honest flat).

## Sentinel methodology (the paper's methods section)

Three instrumentation defects were found by planted sentinels (dead
params reading structure) and live row-level checks — none by code
review, none by unit tests:

1. Frozen reads (bench-generic ≤0.2.0): GET returned stored snapshots;
   quiescent receivers read pre-push values. Fix: recompute-on-read.
2. Warmup race (breeder ≤0.150.1): receivers kept optimizing inside
   their own warmup while senders probed; first probe block contaminated
   (run 23 param_0@50 −0.68). Fix: listening from trial 1, warmup gate
   removed — a deletion, not a patch.
3. Median poisoning (all characterization runs pre-Aug-22): the sender's
   pause self-reads entered receiver_observations untagged (mode 'hold'
   collision) and causal's window query filtered by time only — mixed
   medians halved carrier amplitudes and fabricated +0.339 on a dead
   param (run 23). Fix: lease_phase write gate + receiver-rows-only SQL.

Claim for the paper: honest bars are necessary, not sufficient — bars
quantify repeatability, not attribution. Validity comes from planted
sentinels; each new claim must re-validate its own measurement chain.

## Boundary map (OWED — the sweep)

Not yet collected. Planned grid: carrier amplitude × noise σ × edge
strength × shape {threshold, saturation} × channel count. This file's
rows are all at amplitude 1.0, σ=0.02, edge 0.7 — one point of the grid.

## Raw data

- run24_curves.json, run25_final_curves.json, run26_final_curves.json,
  run29_final_curves.json — final /curves exports per run (this dir)
- CI run logs (permanent): godon repo Actions runs 32566984002 (run 26),
  32574406990 lineage for 24/25/27/28/29
- Loki full-trace extracts preserved on the runner under /tmp (ephemeral)
