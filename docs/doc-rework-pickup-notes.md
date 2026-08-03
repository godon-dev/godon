# Documentation Rework — Session Pickup Notes

Status: PAUSED. Landing page done (PR #80). Full doc rework pending.
Priority shifted to technical work (greenhouse experiment).

## The New Framing (Converged After Extensive Iteration)

**Title:** Open Source Live Systems Tending and Causal Apprehension Engine

**Subtitle:** An engine that apprehends live system dynamics through
driven pressure — and tends what it reveals toward better operating
points. Guiding Human + AI Mind co-pilots to empirical comprehension
and steering.

**Seven key concepts (the "Why Godon?" bullets):**
1. Reveals hidden coupling — autonomous processes silently corrupt each other through shared substrate
2. Transitive topology discovery — discover internal live system interplay topology from behavior
3. Causation, not correlation — real counterfactuals through experimentation, not inference
4. No upfront modeling — the live system is the model
5. Breeder agents — safe, guarded, rollback-capable, probe and tend in production
6. Co-pilot validation — human and LLM intuition tested against reality, kept if better
7. Isolation certification — the same signal that finds coupling can prove absence

**Key terminology decisions:**
- "Tending" not "optimization" as the primary verb
- "Apprehension" for the understanding-through-active-engagement concept
- "Driven pressure" for the perturbation mechanism
- "Steering" not "control" (system is partially autonomous)
- "Cultivation" used sparingly, without "living systems" qualifier
- "Auto-tending" acceptable as compound term
- "Optimization" demoted — it's a mode of the breeder, not the headline

## What's Done

- GitHub org profile (godon-dev/.github, profile/README.md) — SHIPPED.
  Single commit, godon-robot[bot] author. Concise bullets matching the
  framing above.
- Documentation landing page (godon-documentation, material/docs/index.md) —
  PR #80 open on feature/landing-page-rework branch. Header card with DNA +
  gears icons, seven concise "Why Godon?" bullets. Not yet merged.
- Strategic analysis notes (godon/docs/strategic-analysis-notes.md) —
  internal only. Seven strategic angles (side-channel detection, isolation
  auditing, trial data as moat, diagnostics entry point, economic
  externality, counterfactuals, timing window). Plus scalability analysis,
  known code gaps, priority assessment.

## What's Pending — Full Gap Analysis (Prioritized)

### CRITICAL — directly contradicts new landing page

**1. purpose.md — FULL REWRITE NEEDED**
- Currently: "systematic optimization engine," "empirical validation layer
  for AI co-pilots," Human→LLM→Godon→Reality pipeline
- Needs: tending/apprehension framing, driven pressure, topology discovery
  as headline. LLM co-pilot angle stays but as secondary, not primary.
- This is the most-read positioning doc. Needs Matthias's voice — draft
  then review, don't auto-apply.

**2. Four blog post footers — MECHANICAL FIX**
- All end with: "godon is an open-source optimization engine for live systems"
- Files:
  - material/docs/blog/posts/2026-06-07-from-systems-engineering-to-systems-cultivation.md
  - material/docs/blog/posts/2026-06-07-why-intelligence-isnt-enough.md
  - material/docs/blog/posts/2026-06-07-transitive-topology-discovery.md
  - material/docs/blog/posts/2026-06-07-who-optimizes-the-optimizer.md
- Replace with new tagline. Blog bodies are actually well-aligned — only
  footers conflict.

**3. comparison.md — DEFECTS + REFRAMING**
- Duplicated Akamas section (lines ~148-160 and ~162-174, verbatim copy)
- Empty StormForge header (line ~176) with no content
- Every comparison row is optimization-only vocabulary
- GAP: no rows for interference detection, topology discovery, isolation
  certification — the actual differentiators

### HIGH — structural gaps

**4. Observer missing from architecture.md**
- getting_started.md deploys godon-godon-observer pod
- concept_interference_detection.md depends on observer
- architecture.md has NO observer component
- Observer code: godon-images/images/godon-observer/src/ (Rust, optuna_reader.rs)

**5. concept_breeder.md — no mention of probing/watermarking**
- Currently frames breeder purely as "pluggable optimization driver"
- Never mentions watermark injection, mode toggle, or detection role
- The headline capability (perception through perturbation) is disconnected
  from the core concept doc
- Breeder code: godon-breeders/engine/breeder_worker.py (1030 lines)
- Watermark code: godon-breeders/engine/watermark.py (multi-frequency,
  collision-free prime period slots)

**6. MCP tools (mcp.md) expose no detection/topology/isolation query**
- Co-pilots can't apprehend causal structure through MCP today
- Tool list: breeder_*, credential_*, health — no observer/detection tools
- MCP code: godon-images/images/godon-mcp/src/tools.rs

### MEDIUM

**7. references.md — wrong citations for new framing**
- All evolutionary algorithm / parallel multi-objective papers
- Missing: causal inference, spectral analysis, watermarking,
  signal-through-hostile-channels, permutation testing
- open_research.md already invokes seismology/sonar/radar analogies —
  those references belong here

**8. config_guide.md — old vocabulary, missing config sections**
- Says "optimization run" throughout
- No watermark/observer/detection configuration examples

**9. concept_reconnaissance.md — observer/recon confusion**
- Doesn't distinguish per-trial reconnaissance (metric collection) from
  cross-breeder observer (watermark recovery, spectral detection)

### LOWER

**10. Minor vocabulary instances**
- blog/index.md tagline says "future of optimization"
- api.md frontmatter says "optimization runs"
- getting_started.md hedging: "godon is more than interference detection —
  it's a platform for optimization campaigns"

## Suggested Approach When Resuming

1. Start with purpose.md — draft, review, converge. This sets the pattern.
2. Apply blog footer fix (mechanical, 4 files).
3. Fix comparison.md defects (duplicate/empty sections).
4. Add observer to architecture.md.
5. Update concept_breeder.md with probing/watermarking/detection role.
6. Work down the rest.

Each doc needs Matthias's review — don't auto-apply the framing broadly.
The two-hour landing page iteration showed that every word is a decision.

## Technical Roadmap (Agreed Sequence)

1. **Greenhouse impulse experiment** — validate nonlinear channel detection
2. **Close the detection-to-action loop** — detection alone is diagnosis
   without treatment. The full cultivation thesis requires: detect coupling,
   then adapt breeder behavior to account for it.
3. **Tag stable release** — once detection works across complexity spectrum
4. **OSUOSL real-world run** — prove it on real hardware, then the demo
   becomes "we found hidden coupling AND the system self-attuned"

## The Detection-to-Action Loop (Open Problem — Big Research Frontier)

Detection tells you coupling exists. Then what? Today: nothing. The breeder
keeps optimizing as if the coupling wasn't there. That's a monitoring tool
with extra steps.

The full thesis — tending, not just perceiving — requires closing the loop.
"Given a coupling topology, how do the breeders adapt?"

### Known Pieces (Already Built)

- Mode toggle (optimize/hold/impulse) — breeder coordination primitive
- detection_rounds table — protocol for organized probing
- CommunicationCallback — trial sharing between breeders
- Watermark slot assignment — collision-free frequency encoding

### Candidate Approaches (Increasing Sophistication)

1. **Parameter constraint** — detected edge means "my param X propagates
   to neighbor B." Constrain X's search range to avoid the coupling channel.
   Simple, conservative, no new architecture.

2. **Coordinated scheduling** — breeders take turns. A optimizes while B
   holds, then swap. Slower convergence but clean measurements.
   detection_rounds protocol already supports this mechanically.

3. **Joint optimization** — A and B share coupling knowledge and optimize
   jointly. A's objective includes "don't degrade B." This is the
   "permeating configuration" from concept_interference_detection.md.

### Why This Is Harder Than Detection

Detection is one-directional: probe, listen, measure. Action is circular:
detect → decide → act → the system changes → re-detect → the topology
itself shifts because the breeders' adaptation changed the coupling
dynamics. The system you're observing co-evolves with your intervention.

Open questions (not exhaustive — there is likely much more to this):

- Stability: does parameter constraint create oscillation? A constrains X,
  which changes the coupling, which changes what B should do, which changes
  what A should constrain...
- Multi-hop: if A→B→C, does A's adaptation for B account for the downstream
  effect on C? Or does each breeder only optimize locally?
- Intensity threshold: at what coupling strength does action become
  necessary? Weak coupling might not warrant intervention.
- Topology drift: the coupling topology changes as breeders adapt. When do
  you re-probe? Continuously? Periodically? On-demand?
- Non-stationarity: the "non-stationary channel" problem from
  detection_capabilities.md applies doubly here — not just detection but
  the coupling itself shifts.
- Game theory: if each breeder acts in its own interest given coupling
  knowledge, is the resulting equilibrium Pareto-optimal? Or does
  selfish adaptation lead to worse outcomes for all?
- Meta-level: who decides the coordination strategy? The breeder itself?
  The controller? An external orchestrator? Different strategies for
  different coupling topologies?

This is likely a multi-phase research effort in itself. Detection was
phase 1. This is phase 2. The docs hint at it ("permeating configuration",
"temporal dynamics") but don't tackle it.

### Connection to Existing Docs

- concept_interference_detection.md "Outlook" section lists intensity
  measurement, topology, per-parameter tracing, permeating configuration,
  temporal dynamics — all prerequisites or components of the action loop
- open_research.md "Meta-Optimization" section touches on the system
  optimizing its own parameters — related but different (that's tuning
  godon's internals, this is godon tuning the external system based on
  what it detected)
- The "coordination" direction in blog posts is aspirational — "once
  interference is detected and measured, agents can adapt"

The docs correctly identify this as a future direction. It should stay
marked as future/hypothesis until the detection layer is fully validated
(nonlinear case) and the first action-loop experiment is run.

Key repos:
- godon-breeders/ — Python, the breeder engine (breeder_worker.py, watermark.py,
  communication.py, strain_loader.py). sudo access needed (owned by uid 1000).
- godon-controller/ — Python, lifecycle management (breeder_service.py,
  database.py, config.py)
- godon-images/ — Rust (godon-observer, godon-api, godon-bench-greenhouse,
  godon-bench-microgrid, godon-cli, godon-mcp)
- godon-charts/ — Helm chart (values.yaml, Chart.yaml)
- godon/ — bench scenarios + docs (internal notes only, public docs in
  godon-documentation/)
- godon-documentation/ — mkdocs material site (material/docs/*.md are source,
  docs/*.html are rendered output)

All repos under /projects/. Some need sudo to read (owned by uid 1000,
hermes runs as uid 993).

GitHub App: APP_ID=2594394, INSTALL_ID=102627012. Token via
`/tmp/venv/bin/python /tmp/get_token.py`. Push as godon-robot[bot].
All commits need Co-Authored-By: cherusk <10729954+cherusk@users.noreply.github.com>.
