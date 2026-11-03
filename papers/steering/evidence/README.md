# Steering paper — evidence bundles (P4 collection, 2026-11-01/02)

Per-cell bundles for the receipt slots in papers/steering/summary.md.
Every bundle carries: the wish card JSON (the judge book — the verdict
receipt), the wish row, the wishes-list state, tenders, and a readings
strip (node metrics + truth snapshot + drift state at collection time).

## Provenance note (honest)

The collection ran split across two doors. S4, S1, S2-a, S2-b flew in
HAND-FLOWN rooms during the runner outage (godon-test-infra#8: the
2026-11-01 20:46Z nix switch left the runner unregistered; cured
2026-11-02 ~14:29Z by the holder's token refresh + the runner service's
extraPackages fix — kubectl/python3/curl restored to the job PATH).
Hand-flown rooms replicate bench-wish-stack.yml@7748326 step for step
and carry wish/tender ids + timestamps instead of GH run ids. S2-c,
S2-d, S2-e and D2 flew through the workflow door with run ids.

Estate: robots 0.187.2, controller 0.60.21, causal 0.22.32, api 0.0.36
(seeder receipts in each reinstall log). The 2026-11-02 14:41Z
clean-slate reinstall (run 41463883610) separates the hand-flown era
from the workflow era; wishes collected before it are marked in their
meta.json timestamps.

## Cells

- s4-refusal/ — wish b0c8a0c4: refused `outside_measured_range`, named
  (hill [25,75], best branch 0.1184 vs required shift 0.6363, noise
  gate 0.0514), zero actuation (empty card, wish unservable). Plus the
  first-attempt refusal (350c3313, `unmeasured_outcome`) whose cause was
  an operator bug (tender recon URL), banked as the trail it is.
- s1-reflight/ — the godon#399 re-flight trail, five wishes: the
  hold-plan partial-book landing (ed16b651), the +0.10 refusal, the
  full-loop conjunction miss (f3704571: one-dial compose n1->n3->n2,
  predictions 0.6414/0.6491, delivered 0.754/0.758, second-leg error
  ~0.11 vs bars 0.015), shape-(a) `joint_compile_empty`, and
  `position_conflict`. See godon#434 for the two build-level findings
  (hold-plans conclude on partial books; terms never stamp in judge
  books on 0.22.32).
- s2-seeds/ — the S1 shape x5: S2-a landed (notes.md — room purged
  before bundling; numbers from the flight log), S2-b missed (declared
  4h after walks finished, a session-suspension timing artifact), S2-c
  run 41465042445 landed, S2-d run 41467200842 landed, S2-e run
  41469440919 landed. 4/5 landings, repetition bar (3/5) cleared.
- d2-upkeep/ — run 41471550622 (6h watchdog room, scheduled drift door:
  offset_drift_rate 0.0008/tick from tick 1600, cap 0.15): fills at
  room close with the watering economics, the strip log, and the
  post-hoc oracle computed from the /truth recordings.
- figures/ — the five depictions regenerate from these bundles
  (generator scripts live here; captions use public words only:
  promise, band, round, watering).

D1 (drift survival) is NOT re-collected here — its receipts are the
2026-11-01 battery (rooms 19-23, engine-status 2026-11-01 day/evening
entries); the raw cards predate the 11-01/11-02 reinstalls and the
documented numbers + run ids (e.g. 41332501386) are the citable trail.

## 2026-11-02 evening addenda

- s1-reflight/S1v2a-trail + S1v2b-trail: the post-patch re-flights on
  robots 0.187.3 + causal 0.22.33 (robots#302 serve=hold, images#429
  plan receivers — both root-caused via these bundles). S1v2a's card
  carries the first live `kind: term` verdicts of the 0.18x era.
- d2-upkeep/D2-trail: D2 v1 (vacuous-band finding — do-nothing floor
  1.000; strip.log = the 90s sampler: readings/truth/drift/registry;
  d2_oracle.py regenerates the bracket numbers from strip.log alone).
  D2' (hw 0.08, run 41522315492) lands here at its close.

- d2-upkeep/D2pp-trail (2026-11-03, the 4h close at the holder's sealed
  window): the bracket receipt — kept 0.874 (139/159) vs do-nothing
  floor 0.013 vs oracle 1.000; the slide saturated 08:12:45Z;
  compensation continuous (zero discrete waterings; 19 one-minute
  wander straddles; one undecidable blip; no misses; claim judged
  landed n=48). d2pp_oracle.py regenerates every number from
  strip.log alone.
