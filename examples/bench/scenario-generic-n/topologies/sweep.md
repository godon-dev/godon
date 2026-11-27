# The P5 sweep worlds (the campaign's declared materials)

Six checked-in topologies, one per cell, one naming rule:
`sweep-<kind>-0.7-n6.yaml` — dispatch as `family=sweep-<kind>,
coupling_strength=0.7, n=6` on the bench-generic-n room (pinned
godon-bench-generic:0.6.2, frozen for the campaign). Written out by
hand, checked in before flight — the file at the dispatch SHA is what
flew; the PR diff is the receipt. The generator is NOT used here: P5's
cells are bespoke worlds, not a systematic grid (holder's word,
2026-11-20); the base derives from gen_topology.py's mesh-0.7-n6
output, terms from the receipts named below.

## The base world (identical in all six unless the event says otherwise)

6 nodes · 1 dial + 1 objective per node · base linear · weights [1.0]
· edges all-pairs i→j (i<j) at strength 0.7 — 15 edges · noise
gaussian_sigma 0.02. Reference N=6 on the quiet bench (separation
discipline: never the N-ladder rooms). The ONLY difference between
cells is the event block — the controlled variable is the base.

## The cells, in risk order

| file | cell / kind | the event (declared) | clock | first flight? |
|---|---|---|---|---|
| sweep-offsetslide-0.7-n6.yaml | 1 — offset-slide (integration sounding) | node-6 readout slides rate_per_second 0.006, cap 1.0, cued at uptime 420 s (the battery's 0.003/tick, scenario-characterization-offsetstep, at the ~2 ticks/s its terms were declared against — as cell 5 converts it); amended 2026-11-27 from the tick form (rate 0.003/tick, start_tick 360) | wall | flown for years; first on 0.6.2 |
| sweep-gainclimb-0.7-n6.yaml | 2 — gain-climb | node-6 weights 1.0→[[2.0]], at_secs 420, travel_secs 60 (the declared 120 ticks at ~2 ticks/s), then HOLD; amended 2026-11-27 from at_tick 360 / travel_ticks 120 | wall | YES — terms declared, nothing to cite |
| sweep-kneemorph-0.7-n6.yaml | 3 — knee-morph | node-6 base linear→saturation, at_secs 420, travel_secs 60 (240 s from 2026-11-20 to 2026-11-26) | wall | YES — the bench's own blend test names this pair |
| sweep-inversion-0.7-n6.yaml | 4 — inversion | edge node-1→node-6 strength +0.7→−0.7 (through zero, settles inverted), at_secs 420, travel_secs 60 (240 s from 2026-11-20 to 2026-11-26) | wall | YES |
| sweep-evening-0.7-n6.yaml | 5 — multi-event (PRICE, ruled in 2026-11-20) | slide rate_per_second 0.006 cap 1.0 cued at uptime 300s (= the battery's 0.003/tick at the grid's ~2 ticks/sec, declared) · wall weight morph 1.0→1.6 at_secs 600 travel_secs 120 · exogenous step amplitude 0.15 over 60 ticks · officer door-pushes at flight | wall (agent-independent) | YES |
| sweep-transfer-0.7-n6.yaml | 6 — transfer | regime B on ALL nodes, wall clock at_secs 420 travel_secs 60 (amended 2026-11-27 from 360 s: on the cured engine the first map completes at uptime 210–343 s — margins 114 / 150 / 17 s over the 360 s change in the rooms of 2026-11-26 — so 420 = the slowest seen plus ~70 s against boot variance; amended 2026-11-24 from 240 s: on the bench clock the walkers come up ~101 s after the bench, first reading 108 s, first pass ends 289 s — one clean pass under A needs ~290 s, room 45403001197): weights →[[1.5]] + base →saturation; map built under A serves under B — whatever happens is the receipt | wall | YES |

Story alignment (amended 2026-11-27): no cell counts ticks any more.
Cells 1, 2, 3, 4 and 6 ride the wall clock with their change cued at
420 s of bench uptime — after the map builds on the cured engine (the
first map completed at uptime 210 / 246 / 343 s in the rooms of
2026-11-26; 420 = the slowest seen plus ~70 s against boot variance).
Cell 5 keeps its ruled terms (slide at 300 s, morph at 600 s). Before
this amendment cells 1 and 2 were tick-cued at tick 360: on the cured
engine tick 360 arrives at uptime 73–117 s, before any map exists
(before the cure, 222–262 s) — the tick's length is estate load, the
artifact class godon#423 named for drift speed. The tick↔wall relation
is still receipted at flight time from truth (`total_ticks` +
`uptime_secs`; the README-generic clock rule).

## Standing declarations (every room, no silent defaults)

- Uniform bars: the estate settings tree, frozen at spawn (the
  SETTINGS FREEZE line cited in every receipt; convergence guard
  still unbuilt — declared explicitly).
- Truth grades, never self-grading; close-out stamps ride the room.
- Terms in cells 2-6 are the PROPOSED declarations as of 2026-11-20 —
  first flights, nothing to cite; a cell's terms may be amended at
  its turn (one commit, the diff is the receipt), never mid-flight.
- Honest-close rule: a bench anomaly in any cell = receipt + fix +
  re-fly of that cell only.
