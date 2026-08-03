# Detection Architecture — Final Pickup Notes (June 20, 2026)

## Current State

**Breeder 0.109.0** — Block design + DB-backed phase counting
**Observer 0.59.0** — Block step detection with:
- Non-overlapping push/pause windows (by sender timestamps)
- MAD floor 0.01
- Falling edge must be positive (reversibility check)

## What Works

- Block design stimulus: 15 push + 15 pause trials per round ✓
- DB-backed phase counting across parallel workers ✓
- Unique partial index prevents parallel sends ✓
- Fair turn-taking (both breeders become sender) ✓
- Observer detects edges when data is available ✓
- Uncoupled growth_rate shows no false positive ✓
- MAD floor prevents billion-SNR ✓
- Reversibility check prevents temporal drift false positives ✓

## THE REMAINING PROBLEM: Receiver Not Holding During Full Sender Round

The receiver drops out of HOLD before the sender finishes push+pause.
From UI observation (June 20):
- B1 impulse probes are scattered, not in coherent 15-trial blocks visible in UI
- B2 has a huge gap (no trials) from 08:03-08:13
- Receiver enters RECOVER/OPTIMIZE while sender is still in push or pause
- Detection can't work because receiver values during pause period are missing

Root cause hypothesis: The detection_rounds table marks the round as
"active" from sender_push through sender_done. The receiver checks
_any_active_round() each trial. If the sender's round completes (SENDER_DONE)
while the receiver is still measuring the pause effect, the receiver sees
no active round and enters RECOVER.

But the sender's pause block is PART of the sender round. The detection_rounds
table should stay active until SENDER_DONE (after pause completes). Need to
verify this is actually happening.

Debug data (coord_state, coord_debug on every trial) is available to trace
exact timing.

## Next Session Priorities

### 1. Fix receiver hold timing
- Trace coord_state/coord_debug to find when receiver exits HOLD
- Ensure receiver holds for entire push+pause+done cycle
- The sender round (detection_rounds active) must span push through pause to done
- Receiver must not enter RECOVER until sender's SENDER_DONE completes

### 2. Fix trial gaps
- B2 had no trials from 08:03-08:13 — investigate why
- Could be DB query latency (3 DB roundtrips per trial now)
- Could be guardrail failures causing trial FAILs
- Could be Windmill worker scheduling gaps

### 3. Verify push/pause block visibility in UI
- The dashboard may not correctly render impulse_phase=push/pause
- Need to check isActiveImpulse/parseWmMeta functions in dashboard.html
- These were written for ping/listen, not push/pause

### 4. Run clean validation once timing is fixed
- Coupled (0.9): should detect step in growth_rate during push, recovery during pause
- Uncoupled (0.0): should NOT detect

## Infrastructure Notes

- YugaByte 2.19.3: advisory locks unsupported. Unique partial index works.
- Trial state: text 'COMPLETE', not integer 1.
- DB queries needed for: trial count, phase count, round management.
- detection_rounds persists across restacks.
- Breeder tags: bare version numbers.
- ALL commits: godon-robot[bot] as author, cherusk as co-author.

## Version History

Breeder: 0.99→0.100→...→0.108(block design)→0.109(DB phase count)
Observer: 0.54→...→0.57(block step)→0.58(pause windows+MAD)→0.59(reversibility)
