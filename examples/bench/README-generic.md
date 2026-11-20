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

## The event grammar (bench 0.6.x — the campaign freeze)

Every world change is an event with the same shape: **a target, a
trajectory on a declared clock, a destination it settles at, and a cue.**
Travel on the "tick" clock advances with global ticks (activity-paced —
the world changes as it is used); on "wall" it advances with bench uptime
(agent-independent — the world changes on its own). The cue and the
travel each run on the declared clock. Every event's arithmetic is pure
in (uptime, ticks); truth reports the world as it effectively IS.

| change | declared (config) | by hand (door) |
|---|---|---|
| readout offset slide | `drifts: [{rate_per_second, cap, when}]` (wall) or the legacy `offset_drift_rate/cap/start_tick` | `POST /{node}/drift/start {"rate_per_second", "cap"}` |
| node shape (weights / base) | `morphs: [{at_tick, travel_ticks, target_weights?, target_base?}]` — add `clock: "wall"`, `at_secs`, `travel_secs` for wall-paced travel | — (declared only) |
| coupling strength | edge `target_strength` + `at_tick`/`travel_ticks` (or wall fields) — travels from `strength` to the target, then HOLDS; a negative target passes through zero and settles inverted. Legacy `drift_rate` (unbounded) kept; declaring both fails at boot | — (declared only) |
| noise width | `noise.target_gaussian_sigma` + `sigma_at_tick`/`sigma_travel_ticks` (or wall fields) — the readings get fuzzier, then settle | — (declared only) |
| outside push | `exogenous: [{kind: step\|sine, amplitude, objective, at_tick, travel_ticks}]` — step settles; sine stays bounded ±amplitude | `POST /{node}/exogenous/start {"kind","amplitude","objective","travel_secs"}` |

**Boot fails loud on:** an edge declaring both `target_strength` and
`drift_rate`; wall-clocked events missing `at_secs` or `travel_secs`
(declare 0.0 deliberately for an instant step); unknown `kind` or
`clock` strings; a windowless sine (it would read as exactly 0).

**Truth (`GET /{node}/truth`)** carries the effective world at the
instant: objectives, effective weights, base blend (from/to/progress),
`offset_effective`, `noise_effective`, `exogenous_effective`, signed
edge strengths, `total_ticks`, and `uptime_secs` (the wall stamp —
receipts convert clocks via the room's measured cadence).

**Wire tests** in the bench crate drive the real router with real
requests (truth field set, apply shape, door semantics, 404s) — the
struct-vs-wire gap class is gated at CI. The **grammar acceptance
cell** (`.github/workflows/bench-grammar-acceptance.yml`) receipts
every behaviour on the estate; re-fly it on deliberate grammar
changes.
