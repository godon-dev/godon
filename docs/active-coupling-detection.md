# Active Coupling Detection

> **Update (June 2026):** Watermark-based detection (FFT + Rayleigh) has replaced
> the ABA approach described in this document. The watermarking method is validated
> at 6-breeder scale with coupling_factor=0.9. See
> `watermarking-and-causal-discovery.md` for the current approach and validation
> results. This document remains as a design reference.

Design document for controlled coupling detection in the godon platform.

## Background

Statistical coupling detection (observer 0.5.0–0.8.0) was abandoned due to
unresolvable false positives. See `coupling-detection-statistical-methods.md`.

The core insight: observational inference (quality-to-quality correlation)
cannot distinguish "both breeders improving independently" from "breeders
coupled through the target." No statistical method, threshold, or
preprocessing can fix this confounding.

The only reliable signal is a **counterfactual**: observe what happens when a
breeder's influence is removed. This document describes how to produce that
counterfactual through coordinated breeder choreography.

## Core Concept

A breeder normally runs **effectuation** (send parameters to target) then
**reconnaissance** (read quality from target). For coupling detection, a
breeder enters **observe-only mode**: it stops effectuating but keeps
reconnoitering. It measures what the target does *without its influence* while
other breeders continue normally.

Observe-only is the only pause mode. Full stop (no recon, no effectuation)
is not used. The observe-only data is valuable — the paused breeder sees its
own quality shift caused purely by other breeders. This is the coupling signal.

## Certainty-Driven Design

The entire system is driven by a single metric: **certainty**. Certainty is
not a statistical confidence interval or a p-value. It is **measurement
reproducibility** — "do I get the same answer when I repeat the experiment?"

Each choreography is a direct, controlled measurement. Repeating it produces
a new measurement. Certainty is the fraction of consecutive measurements that
agree:

- **All agree** on coupling magnitude (within 20%) and direction → high certainty
- **Some disagree** (outlier among consistent results) → medium certainty
- **No two agree** → low certainty

Certainty drives three things:

1. **Choreography intensity** — low certainty → more ABA cycles, longer phases.
   High certainty → fewer cycles, shorter phases. The system escalates and
   de-escalates automatically.
2. **Frequency** — low certainty → run again soon. High certainty → wait
   longer between choreographies.
3. **Operator signal** — "certainty 92% — picture stable" vs "certainty 35% —
   picture unclear, more data needed."

There are no fixed thoroughness levels. Intensity is emergent from certainty.
There are no thresholds to tune. The metric is reproducibility of direct
measurement — if three choreographies agree, that's high certainty regardless
of the absolute magnitude values.

## Choreography Protocols

### ABA (Single Pair)

The basic building block:

```
Phase A (baseline):     All breeders active, N trials
Phase B (intervention): Breeder X observe-only, N trials
Phase A (recovery):     All breeders active, N trials
```

During phase B, measure:
- Breeder X's quality *without its own influence* (sees other breeders' effect)
- Other breeders' quality *with X absent* (sees if they change)

One ABA cycle is one measurement. Multiple cycles are independent
replications that feed certainty.

### Round-Robin (N Breeders)

For `M` active breeders, run ABA for each breeder in turn:

```
Cycle 1: Pause A, observe B..M
Cycle 2: Pause B, observe A,C..M
...
Cycle M: Pause M, observe A..L
```

This produces a full coupling matrix: every pair, both directions, with
magnitude. Total cost: `M × 3 × N` trials for a single round.

### Adaptive Intensity

The system adjusts choreography intensity based on certainty:

| Certainty | ABA cycles per choreography | Phase length | Behavior |
|-----------|----------------------------|--------------|----------|
| 0–30%     | 5                          | 10 trials    | Aggressive — establish baseline |
| 30–70%    | 3                          | 7 trials     | Moderate — confirm pattern |
| 70–100%   | 1                          | 5 trials     | Light — verify stability |

When certainty drops (picture destabilized), intensity escalates. When
certainty rises, intensity reduces. No operator configuration needed.

Phase length is measured in wall-clock time for heterogeneous breeders
running at different speeds. A "10-trial phase" becomes "wait until the
slowest breeder completes 10 trials, or T seconds, whichever comes first."

## Coordination Between Breeders

Breeders are flat peers — no master, no controller involvement. Coordination
happens through the **shared meta-db** (Optuna RDB storage), the same channel
already used by `CommunicationCallback` for trial sharing.

### Choreography State

Any breeder can write a choreography claim to the meta-db:

```
{
  "choreography_id": "uuid",
  "type": "aba" | "round-robin",
  "participants": ["breeder-A", "breeder-B"],
  "phases": [
    {"phase": "A", "mode": "active", "breeder": null, "duration": 10},
    {"phase": "B", "mode": "observe-only", "breeder": "breeder-A", "duration": 10},
    {"phase": "A", "mode": "active", "breeder": null, "duration": 10}
  ],
  "current_phase": 0,
  "started_at": "timestamp",
  "status": "running" | "completed" | "aborted",
  "results": []
}
```

The claim does not specify a fixed intensity level — the initiating breeder
determines ABA cycles and phase length from the current certainty state.

### Initiation

When a breeder decides a choreography is due (see triggering below), it:

1. Reads meta-db for any active choreographies involving the same breeders
2. If none, writes a new choreography claim
3. Other participants read the claim on their next trial cycle and comply

Conflict avoidance is simple: only one choreography per set of participants at
a time. A breeder seeing an active claim for itself waits until it completes.

### Who Initiates

Any participant can initiate. In practice, the first breeder to notice that a
choreography is due writes the claim. Since all breeders share the same
schedule logic, they'll all reach the same conclusion around the same time —
first writer wins, others see the claim and comply.

## Triggering and Adaptive Frequency

### Modes

- **Active**: automatic monitoring. Choreographies run at an adaptive interval
  with adaptive intensity. Manual trigger always available.
- **Inactive**: no automatic choreographies. Manual trigger only.
- Manual trigger is never disabled.

Active is the default for new scenarios.

### Adaptive Frequency

The system adjusts interval based on certainty:

1. **No data** (certainty 0%): run at `min_interval` (default: 10 minutes)
2. **Certainty rising** (consecutive choreographies agree): interval extends
   — 10 → 20 → 40 → 60 minutes
3. **Certainty dropping** (picture destabilized): interval contracts back down
4. **Ceiling**: `max_interval` (default: 120 minutes) — never wait longer

The interval adjustment is continuous, not stepped. Each completed
choreography recalculates certainty, which determines the next interval.

### Certainty Calculation

After each choreography, compare its results to previous runs:

- **Magnitude consistency**: coupling magnitudes agree within 20% → certainty
  increases
- **Direction consistency**: same dominant direction across cycles → certainty
  increases
- **Magnitude shift**: coupling magnitude changed by >30% → certainty decreases
- **Direction flip**: dominant direction reversed → certainty drops sharply
- **Natural experiment corroboration**: join/leave event agrees with
  choreography → certainty increases. Disagrees → certainty decreases.

The certainty formula is straightforward: it is the fraction of recent
choreographies that agree with each other. No models, no distributions, no
p-values. "Do I keep getting the same answer?"

The pilot sees certainty as a single number (0–100%). When satisfied, they
deactivate auto mode. No automatic deactivation — the human decides when the
picture is stable enough.

### Natural Experiments (Passive)

In addition to deliberate choreographies, the system detects and records
natural breakpoints:

- Breeder joins (first trial submitted)
- Breeder crashes/restarts (gap in trial submissions)
- Breeder count changes

When a natural breakpoint is detected, quality deltas for all other breeders
are recorded in the same coupling-result format. These are free data points
— no disruption, no coordination. They contribute to certainty alongside
deliberate choreographies.

Natural experiments alone are not definitive (the change may be coincidental
with other factors) but they corroborate or contradict choreography results
at zero cost. A natural experiment that agrees with choreography results
increases certainty. One that disagrees decreases it.

### Manual Trigger

The manual trigger serves one purpose: "I want a definitive answer now." It
forces a high-intensity choreography (5 ABA cycles) regardless of current
certainty or interval. Use cases:

- After a deployment or config change
- After adding/removing a breeder
- When the operator suspects something the adaptive schedule hasn't caught yet

Available via dashboard button or CLI command. Overrides active/inactive mode.

## Measurement

### What to Measure

During an ABA phase B (breeder X observe-only):

- **X's quality without X's effectuation** — shows target's natural state
  under other breeders' influence only. Compare to phase A quality.
- **Other breeders' quality with X absent** — shows if X was helping or
  hindering. Compare to phase A quality.

### Metrics per Pair

For each ordered pair (A→B), compute:

| Metric           | What it captures                               | Computation                          |
|------------------|------------------------------------------------|--------------------------------------|
| Quality shift    | Did B's quality change when A paused?          | Cohen's d between phase A and B      |
| Variance shift   | Did B become more/less stable?                 | Variance ratio (phase B / phase A)   |
| Slope shift      | Did B's convergence rate change?               | Difference in regression slopes      |

**Primary metric: slope shift.** It's least sensitive to absolute level
fluctuations and captures whether A helps or hinders B's convergence. A
positive slope shift means B converges faster without A — A was hindering
(constructive interference in reverse). A negative shift means B converges
slower without A — A was helping (positive coupling).

### Per-Objective Granularity

Coupling magnitude is reported per-objective where possible. One breeder may
affect another's energy objective without touching water quality. The composite
quality coupling is derived from individual objectives.

### Result Format

```
{
  "choreography_id": "uuid",
  "pair": ["breeder-A", "breeder-B"],
  "direction": "A→B" | "B→A" | "bidirectional",
  "magnitude": {
    "quality_shift": 0.42,
    "variance_shift": 1.15,
    "slope_shift": -0.08
  },
  "per_objective": {
    "energy": {"slope_shift": -0.12},
    "water": {"slope_shift": 0.01}
  },
  "certainty_contribution": 0.15,
  "timestamp": "..."
}
```

## Engine Changes

### Observe-Only Mode

Add an `_observe_only()` method to `BreederWorker` that:

1. Calls the recon script (same as `_execute_trial` does today)
2. Does NOT call the effectuation script
3. Does NOT go through Optuna ask/tell
4. Reports the observation with a phase marker to the observer

The existing `_execute_trial()` in `breeder_worker.py:279-329` already
separates the two calls — extract the reconnaissance call (lines 312-315)
into a standalone method.

### Main Loop Modification

The run loop (breeder_worker.py:695-755) needs a phase check:

```
on each iteration:
  check meta-db for active choreography involving this breeder
  if this breeder is in "observe-only" phase:
    _observe_only()
  else:
    normal ask → suggest → execute_trial → tell cycle
```

### Phase Reporting

Each observation/trial includes metadata:

```
{
  "breeder_id": "breeder-A",
  "trial_number": 42,
  "phase": "active" | "observe-only",
  "choreography_id": "uuid" | null,
  "quality": {...}
}
```

The observer stores and exposes this so the dashboard can render phases.

## Observer Changes

### API

New endpoints:

- `GET /api/choreographies` — list past and current choreographies
- `GET /api/choreographies/{id}` — choreography detail with results
- `GET /api/coupling-matrix` — current coupling state across all breeders
- `POST /api/choreographies/trigger` — manual trigger (body: breeder IDs)
- `GET /api/coupling-certainty` — certainty scores per pair

### Data Storage

Choreography state and results are stored alongside trial data. The observer
already persists trials — choreography metadata is an additional field on the
trial record.

## Dashboard Rendering

### Breeder Detail View

- **Phase bar**: thin strip above the quality timeline showing colored segments
  — active (green), observe-only (blue), gap (gray)
- **Trial dot styling**: solid dots for active trials, hollow/ringed dots for
  observe-only observations
- **Phase labels**: hover over a phase segment to see "ABA cycle 2, breeder-A
  observe-only"

### Cross-Examination View

- **Coupling matrix**: heatmap showing per-pair magnitude and direction
- **Certainty indicator**: per-pair certainty score (0–100%)
- **Choreography history**: timeline of past choreographies with results

### Coupling Detail View

- **Per-objective breakdown**: which objectives are coupled, which aren't
- **Historical magnitude**: coupling strength over time (is it growing?)
- **Natural experiments**: markers where breeders joined/left, with observed
  quality deltas

## Multi-Breeder Scaling

### Round-Robin Ordering

For M breeders, an M-breeder round-robin produces M×(M-1) directed pair
measurements. Ordering does not matter — each breeder pauses independently,
others are measured. Breeder ID ordering determines pause sequence.

### Concurrency

Only one breeder observes-only at a time. Simultaneous pauses would confound
the measurement — you wouldn't know which paused breeder caused which effect.

The choreography claim enforces this: each phase specifies exactly one
observe-only breeder.

### Scaling Cost

| Breeders | Pairs | 1 ABA, 5 trials | 3 ABA, 7 trials | 5 ABA, 10 trials |
|----------|-------|-----------------|-----------------|------------------|
| 2        | 2     | 30              | 84              | 150              |
| 3        | 6     | 90              | 252             | 450              |
| 5        | 20    | 300             | 840             | 1500             |

The adaptive intensity keeps cost manageable — high-certainty pairs get light
checks, only uncertain pairs get aggressive measurement.

## Failure and Edge Cases

### Breeder Crashes Mid-Choreography

The choreography claim has a timeout. If the observe-only breeder stops
reporting (crashed), the other participants detect the timeout after a
configurable period and the choreography is marked `aborted`. Results
collected so far are preserved. A new choreography can be initiated later.

### New Breeder Joins Mid-Choreography

The new breeder is not a participant in the current choreography — it's
ignored until the next one. Its trial data is still collected and may
contribute to natural experiment analysis (a join event was observed).

### All Breeders Paused Simultaneously

Cannot happen. The choreography protocol pauses exactly one breeder at a
time. The claim structure enforces this.

### Breeder Refuses to Comply

A breeder that doesn't read or honor choreography claims simply continues
effectuating. This invalidates the measurement for that cycle. The system
detects non-compliance (breeder continued effectuating during its observe-only
phase) and marks the cycle as inconclusive. This shouldn't happen in normal
operation since all breeders run the same engine code.

### Recon-Only Observations and Optuna State

Observe-only observations do NOT go through Optuna ask/tell. The sampler
is unaware of them. This is intentional — the observation is not a trial, it's
a measurement. The sampler's state remains consistent. The gap in trial
numbers during observe-only phases is expected and harmless.

## Configuration

```yaml
coupling_detection:
  mode: active              # active | inactive
  min_interval: 600         # seconds (10 minutes)
  max_interval: 7200        # seconds (120 minutes)
  natural_experiments: true # detect and record join/leave events
```

Three settings. Intensity, frequency, and phase duration are all emergent
from certainty — no knobs to configure.

Manual trigger overrides all config — it runs immediately regardless of mode
or interval, at high intensity (5 ABA cycles).

## Implementation Sequence

1. **Engine: observe-only method** — extract recon from `_execute_trial`,
   add `_observe_only()`, add phase reporting to observer
2. **Engine: choreography loop** — read/write choreography claims from
   meta-db, phase-aware main loop
3. **Observer: API and storage** — new endpoints, choreography metadata on
   trials, coupling result storage
4. **Observer: certainty calculation** — compare choreography results,
   compute reproducibility, store certainty scores
5. **Observer: natural experiment detection** — detect join/leave/crash
   events, record quality deltas, feed into certainty
6. **Dashboard: phase rendering** — phase bar, hollow dots, phase labels
7. **Dashboard: coupling results** — matrix, certainty, per-objective detail
8. **Adaptive frequency and intensity** — certainty-driven interval and
   cycle count adjustment in engine
9. **Manual trigger** — CLI command and dashboard button

Steps 1-2 are engine changes in godon-breeders. Steps 3-7 are observer
changes in godon-images. Step 8 spans both. Step 9 adds a CLI command in
godon-cli.

## Open Questions

- **Certainty formula details** — the agreement threshold (20% magnitude, 30%
  shift) needs tuning against real data. Start simple, iterate.
- **Coupling magnitude units** — slope shift is in quality-per-trial units.
  Should it be normalized? Compared to the breeder's own optimization slope?
  Raw numbers may be hard for pilots to interpret.
- **Multiple targets** — if breeders target different systems but share
  infrastructure, the coupling magnitude is expected to be small. Does the
  system need to distinguish "no coupling" from "weak coupling" or is the
  magnitude itself sufficient?
- **Ceiling behavior** — at certainty 100%, does the system stop entirely or
  keep running occasional light verifications? Probably the latter, but
  needs a decision.

## See Also

- `coupling-detection-statistical-methods.md` — post-mortem of the statistical
  approach
- `stasis-patterns.md` — forms of stasis in optimization systems
- `context-aware-samplers.md` — context-aware sampler design for coupling-aware
  optimization
- godon-breeders `engine/communication.py` — existing meta-db communication
  between breeders
- godon-breeders `engine/breeder_worker.py:279-329` — `_execute_trial()` where
  recon/effectuation are separated