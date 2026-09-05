# Paper 3 — Composition — FIRST VERSION DRAFTED (Sep 5, 2026)

**Title:** "From Curves to Cascades: Composed Coupling Prediction Among
Autonomous Agents"

- Status: first complete draft. `paper/main.tex`, `paper/main.pdf`
  (10 pp, tectonic-clean), `paper/make_figures.py` (regenerates all
  figures from the evidence bundle), `paper/references.bib`.
- House style per P1/P2: Libertine/newtxmath, empty date, keywords
  below abstract, ORCID, co-author trailer, no engine versions in
  text, run ids as external identifiers.
- Figures: fig1 TikZ referee schematic; fig2 cliff s47; fig3 cliff s48;
  fig4 junction s46 (shared-axis view). All PDFs regenerate via
  `make_figures.py` from `evidence/` alone.

## The single referee rule (stated once, applied everywhere)

z = |direct − composed| / sqrt(σ²_direct + σ²_pred), σ_pred propagated
stage-by-stage in quadrature (map bar at operating point ⊕ local slope
× input bar; bars = max of bracketing flanks). Validated against every
previously certified number: junction s46 11/12 (max z 2.10 at L=0),
cliff_v2 33/34 (miss = the off-park read), cliff s47 11/11, s48 12/12.
Under the strict direct-bar-only variant: 91/97 (junction 8/12,
s48 11/12) — reported in §6.6 as the sensitivity check.

## Campaign totals in the paper

- Referee rows: door-chain 28/28 (4 seeds) · junction 11/12 ·
  cliff 33/34 + 11/11 + 12/12 (3 seeds) → **95/97 within propagated
  2σ**, median z ≈ 0.3.
- Pieces: 34/34, 11/11, 12/12 vs planted; shapes 32/33, 11/11, 12/12;
  poly 12/12 ×2; cliff-v1 salvage 18/18 + 36 pts no phantom.
- Boundary: ≈2 nonlinear hops at σ=0.02 (depth4: 3-hop composes to
  0.001 = 20× below floor; referee honestly vacuous).
- Certification cells (final protocol, fair turn-taking): 4/4 walks,
  rotation verified event-by-event (13 acquires / 10 yields / 22
  denials / handovers 3–7 s / strict alternation), ≈2 h wall-clock per
  4-walker cell. Dead-dial node retires at 6 flat points (max z 1.09
  vs planted zero) — depth-6 scrutiny passed.

## Evidence bundle (papers/composition/evidence/)

- s47: final_curves, rotation_trail, summary, nodes (PR #353) +
  cliff_cert figures (this session).
- s48 (new): final_curves, rotation_trail (direct Loki pull, 135
  events — job-log trace polluted by the open Loki-window bug),
  summary, nodes + cliff_cert figures.
- junction s46 + cliff_v2: raw curve exports with node maps (new).
- Older: composition-gate scripts/curves, junction/cliff_v2 figures.

## Open before submission

1. Seed-matrix sign-off (cherusk): junction at 2 certified-family
   seeds vs cliff 3, chain 4, poly 2 — one more junction dispatch if
   wanted.
2. Door-chain row cites seeds only; pin the certified s42 run id
   (candidates 33169556954 / 33172249837, both seed 42) and bank the
   four door-chain curve exports.
3. Zenodo bundle at submission (P1/P2 drill; DOI + ORCID 0009-0005-
   7399-5584; arXiv needs endorsement).
4. PR for papers/composition/paper/ + PR #353 still unmerged (awaits
   cherusk's validation of the s47 bundle).
