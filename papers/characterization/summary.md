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

## Boundary map (the sweep — COMPLETE, Aug 27)

32 cells across the full grid; master table in `evidence/sweep/sweep.csv`,
per-cell curves + run IDs in `evidence/sweep/cell-*/`. Verdicts: 24
within-bars (max 1.76σ, median 1.03σ), 4 structure-banked, 3
bridge-parked (P3), 1 flat-sentinels-clean. Every sentinel flat.

- **Floor:** 0.1 characterized (3 honest levels); repeatability corner
  re-certified at 0.15σ (r1, seed 43).
- **Noise wall:** σ0.10 certified at 0.5/0.7/0.9 (r3/n2/n3); r3 is the
  same-cell inversion — P1's detection failed 0.5@σ0.10, the walk
  certified it at 0.62σ max.
- **Shapes:** linear/saturation/threshold/polynomial all within bars;
  threshold 0.7 self-allocated 15 levels around the jump (densest
  campaign curve).
- **Structure:** cross-channel (e1, carrier on objective_1, 0.72σ),
  fan-in (e3), fan-out (e5), bidir (e2), diamond (e4), chain (e6) —
  last three banked as P3 bridge data.
- **Non-stationarity:** growing noise within honestly-fattening bars
  (ns1-3, worst point 0.70σ); slow edge-drift structure captured
  (ns4, 13 levels, peak tracks the moving edge); fast edge-drift →
  non-convergence by design, 22-level probe, boundary in data (ns5).
- **Repeatability:** anchor pair (a1/a2) + both boundary corners
  (r1/r2), two seeds each, all within bars.

Incident log (harness-layer only): #318, #320, wedge run #60,
overnight token expiry + queue stall — data unaffected throughout.
Stack: 30+ runs on one installation, no restack needed.


## The composition gate (Aug 23 — first firing, all green)

Chain node-1 —0.7→ node-3 —0.5→ node-2, saturation carriers, 3
breeders (first 3-breeder run; multi-receiver curves merged the same
day). Node-1's single walk measured both the one-hop and two-hop
curves at 9 shared levels; of 36 curves exactly the 3 planted paths
are non-flat.

- **Identity (in-sample):** measured curve(A→B) vs 0.5 × curve(A→C):
  9/9 within 2σ, median deviation 0.18σ.
- **Prediction (out-of-sample, quiet bench, committed first):**
  L=56 → 0.13σ; L=68 → 0.35σ. Both hold.
- **Steering precursor (first ACT):** target −0.100 at node-2, map
  inverted itself to A=32.42, executed, landed −0.1038 → 0.10σ.
  PROBE→MODEL→PREDICT→ACT→COMPARE fired for the first time.

Scope, honestly: quiet bench (no live agents resisting); additive-
linear coupling physics — the METHOD is proven (discovered curves
compose, bars propagate, inversion works); nonlinear composition and
the live-B rung remain open. Evidence: composition-gate-*.json/.py in
this dir; CI run 32637299365 (permanent); verification star runs
32633729366 / 32631063923 / 32630439204.

## Raw data

- run24_curves.json, run25_final_curves.json, run26_final_curves.json,
  run29_final_curves.json — final /curves exports per run (this dir)
- CI run logs (permanent): godon repo Actions runs 32566984002 (run 26),
  32574406990 lineage for 24/25/27/28/29
- Loki full-trace extracts preserved on the runner under /tmp (ephemeral)
