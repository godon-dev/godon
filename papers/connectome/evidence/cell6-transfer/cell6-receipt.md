# Cell 6 (transfer) — run 44811527511, GREEN, the first fully-clean story-window close

## The world: regime A -> regime B, whole-regime
All six nodes morphed at wall 240s over 60s travel: weights 1.0 -> 1.5,
base linear -> saturation (truth-receipted live: base saturation
progress 1.0, effective weights [[1.5]] at uptime 385s). The map was
built under A; the world became B; the room served through it.

## The map's response — rotation widened (vs the inversion's single prober)
Sender profile through the story: 1 sender (quiet) -> 2 senders by
minute 4 post-change -> clean registry purge at close.

## DATA REFINEMENT (2026-11-21 — regenerated from this room's captures)
Sharper than the stamp-coarse read above: the second sender joined in
the CHANGE MINUTE (first two-sender capture at uptime ~235s; cue 240s,
travel 60s), six curves -> twelve at the same step. The paper prints
the data. Mechanism
(code-read, godon-robots engine/src/coordinator.rs): the sender_lease —
ONE holder per group, phase probe_push, heartbeat, budgets; fairness
"starved peer outranks recently served"; detection flags
detection_readiness (the REASON), the lease grant is the ROLE.
Inversion broke ONE member's promise -> one reason -> one prober;
transfer broke ALL SIX -> the lease rotated wider. Counts agree:
685/680/835/675/785/2241 — the long lease holder ran ~3x siblings.

## The close — the story-window fix works end to end
completed/success: stamps restarts 0 / boots 1 (bench 20:27:48 ->
20:38:40, 10.9 min); meters dumped inside the window; cleanup verified
(registry curves purged at close — 0 curves post-room).

## Honest note (officer error, receipted)
Transfer was dispatched while 4c's teardown was still running; the
gate stomped 4c's cleanup (4c -> cancelled). Damage janitorial only:
4c's story + stamps + capture were complete before the overlap.
Serial discipline: ONE dispatch per live room, always.

## What this receipts for the paper
The transfer cell's first live data point in the lineage: a map built
under one regime served under another — event exact, all six walked,
the rotation widened proportionately to the blast radius, and the
close is clean. Curve bodies banked (~15 samples through the story).
