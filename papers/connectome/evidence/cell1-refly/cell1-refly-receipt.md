# Cell 1 RE-FLY (offset-slide) — run 44782221725, 2026-11-20 17:20-17:29Z
VERDICT: RECEIPTED — clean close, all six walked, science on the map.

## The close (green, first of the campaign)
- ALL REACHED 400 (concluded by target, not timeout): trials at close
  415 / 700 / 410 / 415 / 410 / 610 — six of six workers walked.
- Stamps: bench restarts 0, boot lines 1 (one continuous world, boot
  17:20:02 -> close 17:29:27, ~9.4 min room). Cleanup verified gone.
- The re-fly's premise held: on the fresh post-reinstall estate the
  ledger-init race passed 6/6 (last night: 4/6 on the 3-day-old DB —
  root B stands: retry/backoff still owed in the engine).

## The drift, exact again (live truth reads)
- birth ticks=0/uptime 7s; cue visible at tick 386 (offset 0.078 =
  26 ticks past cue x 0.003 exactly); capped at 1.0 by ~tick 693
  (uptime ~253s); held to close. Same arithmetic twice, two rooms.

## The heal-cost signature (first live receipt)
- Siblings parked at 410-415; the DRIFTED node's tender ran 610
  (+~200 trials = the re-walk span), tender-2 at 700 (upstream
  re-pricing under coupling — peer-motion material, cited not claimed).
- Detection machinery ran within the room window on the drifted node
  (readings vs promise while offset slid; the extra trials ARE the
  re-walk). The per-trial value series (readings-vs-truth curve,
  conviction timing) lives in the workers' ledger tables on the
  estate (yugabyte; auth gflags post-reinstall — the dig is the
  evidence-port session's first task, P4 pattern).

## Banked en route
- Cancelled runs lose Actions logs AND artifacts — pull receipts
  BEFORE cancelling (last night's lesson, confirmed by contrast).
- job_logs holds only the tail (~3 trials); full worker logs rotate
  to worker disk — the ledger tables are the durable series.
