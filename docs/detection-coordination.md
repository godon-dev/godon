# Detection Coordination via Breeder Mode Toggle

## Problem

Impulse probing during active optimization fails. The receiver's exploration noise
(std ~0.25) swallows the coupling signal (shift ~0.06, <1 sigma) even at
coupling_factor=0.9 with 4 stacked impulses. The optimizer is nonstationary —
stacking inconsistent signals averages toward zero.

Alternatives exhausted:
- Stronger/longer impulses: still buried in optimizer noise
- Post-hoc correlation: statistical analysis, rejected
- Sinusoidal + FFT: fails on nonlinear channels
- Embedded impulse probing: SNR too low (0.25-0.39 at coupling 0.9)

## Solution

Dedicated detection rounds. Receiver holds params still, sender pushes impulse.
Clean measurement with no optimizer noise.

## Architecture: Same Component, Mode Toggle

No new service. No new component. Breeders read their `mode` from YugaByte
(study metadata) at each trial start. Three modes:

| Mode | Behavior |
|------|----------|
| `optimize` | Normal operation. Run sampler, explore params. Default. |
| `hold` | Freeze current params. Re-submit last known params. Record objectives. |
| `impulse` | Push designated params to upper bound. Single trial. Auto-revert to `hold`. |

The breeder already connects to YugaByte every trial (Optuna study). One
additional read: "what mode am I?" No new connections, no new APIs, no polling
an external service.

## Detection Round Table

A `detection_rounds` table in the breeder's own YugaByte database:

```sql
CREATE TABLE detection_rounds (
  round_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sender_id   UUID NOT NULL,          -- breeder that pushes impulse
  created_at  TIMESTAMPTZ DEFAULT now(),
  status      TEXT DEFAULT 'active'   -- active / completed
);
```

Each breeder checks at trial start:
1. Is there an active round where I'm the sender? → mode = `impulse`
2. Is there an active round where I'm NOT the sender? → mode = `hold`
3. No active round? → mode = `optimize`

The breeder doesn't need to know about other breeders. It just checks:
"am I sender this round?" Yes/No.

## Protocol

### Phase 1: Network Sweep

One sender at a time, all others hold. O(N) rounds.

1. Insert row: `sender_id = breeder_A, status = active`
2. All breeders read the table next trial. Breeder A impulses, all others hold.
3. After one trial cycle, mark round `completed`.
4. Insert row: `sender_id = breeder_B, status = active`
5. Repeat for all breeders.
6. No active rounds → all breeders resume `optimize`.

Who writes the rows? Anything: manual SQL, a Windmill script, the observer
after it sees enough optimization trials. The breeder doesn't care.

### Phase 2: Characterization

Only for sender-receiver pairs where Phase 1 detected coupling.
Same mechanism — detection_rounds table, targeted sender.
Receivers hold. Controller coordinates structured sweeps.

## Breeder Changes

1. New `mode` field in breeder trial loop (read from detection_rounds table)
2. If `hold`: re-submit current params, skip sampler
3. If `impulse`: push params to upper bounds, record, auto-revert to `hold`
4. Optuna study state persists across mode changes — resuming is safe

## Observer Changes

None for Phase 1. Observer reads trial data as usual. Detection rounds produce
trials with `mode: "hold"` or `mode: "impulse"` in watermark metadata.
The stacking logic works on these clean measurements — receiver is stationary,
so one impulse gives a clean signal. No stacking needed.

## Open Questions

- Round creation trigger: after N optimization trials? Manual? Observer-driven?
- How to determine "trial cycle complete" — breeder marks round completed after
  its impulse trial finishes? Or the creator polls?
- Should `hold` mode record the frozen params in trial metadata for observer?
- Multiple impulses per sender in one round? One should suffice (receiver stationary).
