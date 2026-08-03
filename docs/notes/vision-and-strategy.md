# Vision & Strategy Notes

Internal notes — not published. Captured July 2026 session. Everything not in the published docs or the living connectome notes.

## The Optimizer as Instrument

The profound shift: the optimizer stops being a blind search engine and becomes a measurement instrument.

Today the optimizer spends 500 trials exploring a space. Most rediscover structure it found last run. What if instead it spent 50 probes maintaining the model and computed optimal configurations directly from the model?

50 probes instead of 500. The model does the work.

The optimizer doesn't disappear. It changes role — from blind search to targeted probing that maintains the living connectome. The ratio of probing to prediction adapts to the system's structural volatility.

## LLM as Interface Layer

The connectome graph isn't text — it's measured physical relationships with numerical weights and response functions. An LLM is the wrong tool for the math (propagating transfer functions through a graph). But it's the right tool for the interface on top.

The query pipeline: human asks a question in natural language → LLM translates into the right graph query → graph engine computes the exact answer → LLM translates the result back into human language.

The LLM never does the math. It does the translation between human intent and graph query. This is closer to "agentic RAG" or tool use — the LLM calls a function that queries the coupling graph.

Not RAG (which retrieves text). Structured graph query with LLM as language layer.

## GPU Connectome / Hardware Reverse-Engineering

A modern GPU is 80+ streaming multiprocessors, multiple memory controllers, L2 cache slices, ray tracing cores, tensor cores — all sharing power and thermal budgets. The documented architecture tells you the topology. The effective topology — what actually happens under load — is different.

The protocol discovers this: one SM cluster pushes max workload, another holds idle, CFAR detects whether the first's power draw throttled the second's clock. You map the effective power and thermal coupling graph of the silicon — not the architecture diagram, but the real thing.

This isn't about optimizing the GPU. It's about understanding the hardware as it actually behaves. Every GPU is slightly different due to manufacturing variation. The effective model of YOUR specific hardware, not the reference design.

### Degradation Detection

A GPU degrades — TIM dries out, VRMs lose efficiency, fans degrade, solder joints develop micro-cracks under thermal cycling. The effective coupling changes. The spec sheet doesn't update.

The connectome scanner catches this. Probe today, compare to last month's scan. Edge weight increased 40%? That's TIM degradation. New coupling path appeared? That's a hardware fault.

You can't repair silicon. But you can predict failure, compensate (proactive throttling), and diagnose (the coupling fingerprint tells you WHAT changed).

## Organoid Intelligence / Biological Systems

Biological neural networks grown on MEAs (multi-electrode arrays) — currently a black box. You stimulate one electrode, record from all others. But the responses are non-linear, non-stationary (the network adapts and learns), and buried in biological noise.

Our exact problem. Active probing — stimulate strongly at electrode A, hold the network at baseline, measure response at electrode B through CFAR. The coupling graph that emerges is the organoid's effective connectome — not the synaptic wiring, but the functional connectivity.

The non-stationarity is the interesting part — the organoid LEARNS. Its coupling graph changes over time. Continuous probing would reveal plasticity: which connections strengthen, which weaken, how the network reorganizes.

The scanner software exists. The wet-lab interface (simultaneous stimulate-and-record electrode arrays) doesn't. Different kind of engineering — neurobiology, not computer science.

## Probe Cadence / Coupling Spectroscopy

The connectome isn't a fixed property waiting to be measured. It depends on how you probe. Different probe cadences excite different physical coupling mechanisms:

- Slow probes (seconds to minutes): steady-state thermal coupling, conductive transfer
- Medium probes: convective coupling, air exchange, mass transfer
- Fast probes (microseconds to milliseconds): electrical coupling, power delivery, capacitive effects

The connectome at one cadence is one view. A complete characterization requires probing across a spectrum of cadences — coupling spectroscopy.

The probe itself injects energy at a frequency. That frequency interacts with the system's dynamics. In a non-linear system, different excitation frequencies activate different coupling paths.

The implication: the "frozen connectome" is contingent on the probe configuration. It's a valid measurement as seen through that specific probing window, not a universal description.

For most systems, a dominant mechanism exists and one cadence suffices. Complex systems with concurrent coupling paths may require multi-cadence probing.

## Meta-Optimization of Detection

The scanning process has many parameters: amplitude, push/pause duration, which parameters to push, which channels to observe, cadence. Finding the optimal probe configuration is itself an optimization problem.

But it's bounded. The parameter space is small (~5 dimensions). Physical heuristics get you 90% there. Control runs validate. The edge cases where the probe creates false structure are rare and detectable.

The recursion has a floor. The probe optimization is the easiest optimization problem in the whole system.

## Prediction-Driven Rescan

A frozen connectome enables prediction. When the prediction fails, the model is stale.

The prediction error localizes WHERE (which node's prediction is most wrong). It does NOT specify WHAT changed. But it narrows the search from "everything" to "this neighborhood."

Re-probing the neighborhood with the last-known-good cadence handles the common case (edge weight shift). If standard probing fails, multi-cadence exploration reveals whether a new coupling mechanism emerged.

The prediction error is the compass — it points toward ignorance.

## Practical Engineering Roadmap

### Priority 1: Protocol Hardening (days)
- Fix coordination deadlock (readiness barrier stalls ~25% of runs)
- Increase lease duration (90s → 300s)
- Persist coordinator state in DB (survive worker restart)
- Impact: reliable bidirectional detection, reproducible runs

### Priority 2: Falling-Edge Primary Detection (days)
- Current: both rising + falling edges required. Rising misses ~33%.
- Fix: falling edge as primary, rising as confirmation
- Impact: higher single-round detection reliability

### Priority 3: Calibration (weeks)
- Currently bypassed via config hold_params
- Generic case (self-discovery of neutral params) broken — MAX_CALIB_STD=0.05 unreachable for non-stationary systems
- Fix: adaptive calibration criterion based on local drift rate, or LLM-assisted calibration
- Impact: works on any system without manual configuration

### Priority 4: 4-Breeder Topology (weeks)
- Extend simulator for multiple coupling neighbors
- 4 greenhouses in a line topology
- Pairwise detection across all 12 directed pairs
- First real connectome scan of a multi-node system

### Priority 5: Lighter DB Substrate (weeks)
- Make DB backend configurable (YugabyteDB / Postgres / SQLite)
- Same SQL, no code changes
- Impact: faster iteration, smaller footprint, local testing

### Priority 6: Dashboard / Visualization (weeks)
- Coupling graph view (nodes + edges with weights)
- Live scan timeline (side-by-side sender/receiver)
- Prediction layer
- Degradation tracking over time

## Visualization Exploration

### The Connectome Ball

Vision: a 3D animation showing the full protocol. Multiple breeders probing multiple targets. Impulses flowing. Coupling signals traveling. Detection flashing. A connectome ball growing above as a separate construct — a wireframe sphere where nodes and edges materialize as discoveries happen. Sparks arc upward from detection points to deposit new nodes/edges.

### Two-Zone Composition

- Zone 1 (lower): infrastructure + breeders + impulses + coupling. The probing world.
- Zone 2 (upper): connectome construct. A growing graph inside a sphere. Separate from the action below.
- Spark bridges the zones on each detection.

### Visual Language

- Breeder crystals: octahedron geometry, godon logo, color = state, rotation = intensity
- Impulse: sonar ping — sharp expanding ring, continuous stream during push
- Coupling: light pulse traveling between targets
- Guardrails: boundary shimmer on infrastructure when push approaches limit
- Connectome: golden threads + nodes inside a wireframe sphere

### Why It's Hard

Five layers of challenge:
1. Physical world (infrastructure, coupling flow)
2. Protocol (state machine, lease, readiness — abstract concepts to visualize)
3. Data (real CFAR bands, edge weights, detection flashes)
4. Connectome (N-node graph in 3D, building itself)
5. 30-second comprehension for non-experts

Each solvable individually. Together they're a serious project. Needs a UI/UX designer or a model (like GLM-5.2 that wrote the Conservatory) that can produce quality 3D scenes.

### Tools

Three.js (current standard for web 3D visualization). Not the best possible — Bevy/WebGPU is next generation — but the best available for shipping today. The Conservatory proves what's possible with Three.js + bloom + god rays + PBR glass + custom shaders.

Alternative: Blender Python script for cinematic render (MP4, not interactive). Better quality, not web-shareable. Good for presentations/pitches.

Decision: skip visualization for now. Detection result is the product. Visualization is communication. Ship proof first, polish later.
