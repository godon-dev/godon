# Evidence — cert s47: first clean 4/4 cliff certification

Run: [33968683471](https://github.com/godon-dev/godon/actions/runs/33968683471) ·
2026-09-05 · engine: breeder **0.163.3** (turn-fair acquire) · scenario:
**cliff**, seed 47 · iterations.max 2500 · watchdog 300 min (not reached).

**Claim this run feeds:** the fair-share lease — quantum yield + role ledger —
lets all breeders walk and produce converged maps in one cell, end to end,
with the trail to prove it.

## Result

- **GREEN in 2h04m40s** (13:21:55 → 15:26:35 UTC), terminal state — not budget.
- **4/4 breeders walked. 32/32 curves converged** by the priced sufficiency stop.
- Map depths: **6, 8, 11, 11 points/curve** — adaptive: discontinuities
  bisected deep, flat regions priced out early.
- Rotation: **13 acquires, 10 quantum yields, 22 denials** — strict
  alternation, handovers of 3–7 s, every refusal correct. Zero errors.

## Figures

**fig1_maps.png** — the four final maps. White: objective_0. Grey: objective_1.
Thin vertical bars: measurement uncertainty per point. Fog bands: unresolved
gaps that are *cheaper to leave than to ask* (the priced stop working — a
converged curve may still carry questions worth less than their answer).
Read: the cliff's discontinuities are resolved in all four worlds.

**fig2_rotation.png** — the microphone across the run. Triangles: lease
acquires. Diamonds: quantum yields (3 cycles served → hand over). Crosses:
denied re-acquires (holder alive — correctly refused). Squares: walk
retirements. Dots: walk progress in levels/101. The shaded band is the
measured idle tail: **maps were complete at 14:17Z; the cell closed 15:26Z —
69 minutes of park burn.** That band is the convergence-based cell end lever,
now priced on a live cert.

**fig3_depth.png** — map depth per walker, with converged fractions (8/8 each).

## The honest boundary

- **n = 1.** First clean 4/4 certification — not yet a reproduced result.
  Seed 48 was dispatched at write time and decides reproduction.
- The ~2× vs cert-47 (4h05m, 0.161.0) is attributed primarily to the
  **sufficiency stop with the self-curve folded in (0.162.0)** plus **rotation
  carrying all walkers (0.163.x)**. The turn-fair acquire (0.163.3) removed a
  veto that was provably inert in the final smoke (0.0 vs 0.0) — hygiene, not
  horsepower.
- Depth 6 on walker bc12e3ee deserves the reader's eye: its remaining gaps
  priced below the sufficiency bar with the self-curve *included* — the fixed
  guard's verdict, not the old exemption. The gate results at verdict time are
  the check on that.

## Data

- `data/curves_final.json` — final curve state per sender (points, bars, gaps,
  converged), from the run's own `/curves` export, pre-cleanup. Authoritative.
- `data/rotation_trail.json` — 105 timestamped mic events (acquire / yield /
  deny / DONE / init / progress / priced).
- `data/run_summary.json` — phases, counts, durations, receipts.

Source receipts: Loki `{service_name="godon-breeders"}` over the run window;
job log of run 33968683471; seeder env `BREEDER_VERSION=0.163.3` verified.
