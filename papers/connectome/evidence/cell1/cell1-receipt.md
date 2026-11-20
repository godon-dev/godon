# Cell 1 (offset-slide sounding) — run 44759216227, 2026-11-20 15:02–15:50Z
VERDICT: instrument VERIFIED, science re-fly OWED.

## What verified (the sounding's purpose)
- The whole room on the frozen bench 0.6.2: sweep family door, checked-in
  topology boot, 6 targets + 6 tenders, close-out steps.
- Drift arithmetic exact per truth: cued at tick 360, ramped 0.003/tick,
  capped at 1.0 by ~tick 693; offset held; ticks monotone (bench never
  bounced; live reads: 2→927→1257→4473 ticks over 316→988s uptime).
- Room's own cadence ~290-320 ticks/min (2.4x the grid estimate — the
  receipts convert clocks via this room's measured cadence, per README).

## What did NOT land (the science)
- Tenders 5 and 6 never walked: workers failed at
  "ledger init failed: db error | Timed out waiting for 'trials' table
  creation" (SqlState EXX000, pg_client.cc, Yugabyte) — 6-wide concurrent
  ledger inits; 4 succeeded, 2 timed out at the ~3min edge.
  Tender-6 tends node-6 — the DRIFTED node: no readings, no detection,
  no heal. Trial counts at close: n-1 2825, n-2 3756, n-3 2686,
  n-4 3711, n-5 0, n-6 0 (observer metrics; 32 stale series ignored).
- Windmill jobs: all 6 systemtender_worker jobs created 15:02:50–15:03:12
  (v2_job); a4c5+a50b stalled (flat 5MB), 4 walkers ran to cancel.

## Roots (receipted)
A. api 0.0.37 (pre-cure) windmill token died mid-cleanup (3d old) →
   purges 500'd silently → cleanup hung past timeout → run cancelled;
   artifacts/log routes empty for cancelled runs. Pod restart cured the
   door (200). Durable fix: api 0.0.38 ladder (OWED).
B. Yugabyte trials-table creation timeout under 6-wide concurrent ledger
   init (first N=6 room on the post-11-17-reinstall estate). Engine fix
   owed: retry/backoff or pre-create (robots lane).
C. Wedged cleanup leaves walker jobs immortal (kept failing trials
   against the dead bench for an hour+). Cancel via queue flag
   (v2_job_queue.canceled_by) — enforced kill in ~8s, verified tonight
   (4/4 jobs → v2_job_completed). Bank the pattern.

## Honest-close
Re-fly cell 1 after root B's fix. Cells 2-6 hold until then (same class).
