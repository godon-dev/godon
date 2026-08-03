# Session Notes — July 24, 2026

## LEARNED (high confidence — from proof or direct reasoning)

### L1: The contribution is quantification that composes, not hidden coupling discovery
The framing "we discover hidden coupling" was overstressed. The real value: measured coupling precise enough to compose into multi-hop prediction. Known-but-unquantified coupling is an equal or bigger target than hidden coupling. Every system operator knows their racks exchange heat. Nobody has measured the edge weights precisely enough to predict what happens three racks away.

### L2: No human-specified structure anywhere
Every existing modeling method embeds human assumptions (system ID specifies model structure, DCM proposes candidates, analytical modeling writes equations, RL designs reward functions). Godon eliminates human-specified structure entirely. The only human input is the measurement protocol (push, hold, pause) — a procedure, not a policy about the system. This is what makes the method domain-agnostic.

### L3: Metaheuristics optimize the wrong objective
Currently the breeder uses metaheuristics to maximize the system objective directly (growth_rate). This is the wrong target for coupling work. The metaheuristic should serve measurement — exploring the space, generating perturbation data from which coupling is discovered. Once the graph is built, the system optimum is computed analytically from response functions. Metaheuristic optimization on the real system becomes unnecessary for graph-covered territory.

### L4: The local/coupling parameter split is a fiction
Parameters are simultaneously local (heating affects my growth_rate) AND coupled (heating affects neighbor's growth_rate). The measurement agent pushes a parameter and records ALL channels that moved — local and coupling, same probe, same data. The graph contains all measured edges. There is no pre-classification into "graph parameters" and "breeder parameters." The boundary is graph coverage: measured territory belongs to the graph, unmeasured territory belongs to the breeder.

### L5: The graph should be dominant wherever measurable
The connectome covers both inter-node coupling edges AND intra-node local response functions. Once measured, the graph owns the full response surface and computes optima analytically. The breeder's role narrows to frontier exploration (regions the graph hasn't measured) and bootstrap (before the graph exists). The breeder is subordinate to the graph, serving its growth.

### L6: Component separation is a must
The coordinator timing bugs come from forcing measurement inside an optimization loop. The breeder (optimizer) and the measurement agent (designed experiments) must be separate. The measurement agent holds by default — it doesn't resist holding. The breeder yields cleanly when told. Separation eliminates the conflict.

### L7: The Markov blanket is measurement-dependent, not absolute
Statistical independence is a property of the instrument, not the system. It holds where coupling drops below the detection floor. CFAR threshold IS the practical definition of statistical independence. The blanket shifts with sensitivity, noise, probe amplitude, system state. The connectome finds the blanket at current measurement sensitivity — the only blanket that matters.

### L8: Friston's blanket is circular for coupled systems
You cannot define the correct blanket without knowing all coupling channels. You cannot assume you know all channels. You cannot prove statistical independence without exhaustively probing — which is the problem you're solving. The practical alternative: define the boundary by control authority and measurement coverage. Each measured edge turns unstructured noise into structured input.

### L9: The system is the sum of its measured relationships
The system's real behavior lives in the relationships, not the parts. Component specifications tell you nothing about coupling. The coupling strength between two nodes emerges from wall thickness, vent positions, crop phase, weather — a combination no individual component model contains. You cannot derive the relationships from the parts. You can only measure them through intervention.

### L10: Forward simulation is iterative propagation, not composition of multipliers
For non-linear systems, edges are state-dependent. Naive multiplication (0.7 × 0.5 = 0.35) fails because intermediate nodes move. The solution is iterative forward simulation (Gauss-Seidel): propagate perturbation through graph, update node states, converge. Same math as circuit simulators, power grid load flow, weather models. Measured edges are jacobian entries — local derivatives at each operating point.

### L11: Metaheuristics are non-committal (policy-free per Talbi)
TPE's density estimate, CMA-ES's covariance — these are internal search dynamics, not persistent deployed strategies. When the optimization ends, they vanish. This distinguishes them from RL where the policy IS the product. The connectome is also not a policy — it's a measured model. No component in the pipeline commits to a permanent strategy.

## UNDECIDED (genuine open questions requiring evidence or decision)

### U1: Component count and boundaries
The system separates into at least three components (breeder, measurement agent, causal). The exact count is not finalized. Potential further separation: maintenance monitor (different cadence), scheduler (air traffic controller), artifact archive (versioned storage). The principle is separation — the specific component list emerges from need.

### U2: Measurement agent name
"Characterizer", "examiner", "surveyor" all considered. Not decided. Currently "measurement agent" in the roadmap.

### U3: Does composition actually work?
The 4-breeder chain test has never been run. Naive composition of pairwise edges may or may not predict multi-hop effects. Iterative forward simulation may or may not converge for greenhouse-level non-linearity. This is the empirical gate. Everything downstream depends on the answer.

### U4: Interaction-mediated coupling tractability
Some coupling only activates when multiple parameters are pushed together (A × B produces coupling that neither produces alone). Characterizing these requires 2D+ sweeps — M² per parameter pair. The ratio of direct vs interaction-mediated coupling in real systems is unknown. If most coupling is direct, characterization is tractable. If dominated by interactions, it may be intractable at scale.

### U5: Breeder mode architecture
Three candidates discussed: (A) graph-only (breeder obsolete after graph), (B) parallel modes (customer chooses), (C) unified pipeline (phases interleave). Decision deferred — depends on composition test result and how much value the breeder adds vs graph computation.

### U6: Characterization protocol specifics
The measurement agent needs a sweep protocol: which parameters, how many magnitudes, how many operating points, how many samples per point. Metaheuristic-driven sampling with hold-and-measure proposed as alternative to deterministic grid. Active information-gain targeting proposed as enhancement. None designed in detail.

### U7: Formal systems as targets
Code mutation detection (mutate compiler rule, observe downstream effects) is a valid application of the method but requires a different detection formulation (differential, not temporal). No CFAR copy-paste. The hiddenness scale says "formal corpus-scale = significant" but the instrument doesn't exist yet. Deferred.

### U8: Generic bench as third bench type
Shipped and compiles. Ground truth for validation. Four scenarios created. But never tested end-to-end with breeders + coordinator + causal. The bench_generic breeder strain has unverified reconnaissance format assumptions (array objective extraction).

### U9: Microgrid bench detection
Never tested. Different channel type than greenhouse (approximately linear). Same method, untested parameters. Needed for cross-channel validation claim in the paper.

## SPECULATIVE (plausible, explicitly open to being wrong)

### S1: Coupling patterns generalize across domains
If 50 connectomes are accumulated across domains (greenhouses, data centers, power grids), universal patterns MAY emerge: cascade signatures, phase transition dynamics, critical coupling thresholds, cross-scale nesting. This follows the arc of every measurement science (astronomy, crystallography, genomics). But the data doesn't exist yet. Patterns may not emerge. The only way to find out is to build the instrument and accumulate.

### S2: The connectome as a new kind of language
A coupling graph compresses a system's behavior into a transferable notation — like musical notation or DNA. Accumulated connectomes could develop a "grammar" of coupling patterns. A new scan read against the grammar reveals anomalies. This is the far edge — requires accumulation, which requires deployment.

### S3: The breeder as frontier explorer
In the full lifecycle, the breeder explores uncharacterized parameter regions. The graph follows and absorbs the new territory. The breeder and graph co-evolve: breeder extends frontier, graph measures and stabilizes. This cooperation is intuitively appealing but unproven. It may turn out that the measurement agent can explore on its own without the breeder.

### S4: Connectome enables system redesign
"If you can predict what perturbation at node A does to node D, you can find the coupling path that, if modified, would most improve system behavior." The connectome becomes a design tool — remove harmful edges, strengthen beneficial ones, insert decoupling where cascade paths are dangerous. Not just diagnosis but engineering input.

### S5: The blanket redefinition (control-measure boundary)
Defining the system boundary by control authority and measurement coverage (what you control = inside, what you measure = structured input, what you don't measure = noise) may be a genuinely better operational definition than Friston's statistical independence. Each measured edge pushes the practical boundary toward true independence. But this is a reframing, not a proven theorem.

### S6: Metaheuristic objectives shift to meta-objectives
Instead of maximizing growth_rate, the metaheuristic maximizes information gain about coupling structure (coverage, novelty, uncertainty reduction). This is active experimental design. Crude versions (novelty search, diversity pressure) are policy-free. Full Bayesian optimal experimental design is model-driven (policy). The right balance is undecided.

## WHAT WAS SHIPPED THIS SESSION

- godon-causal 0.1.0 released to GHCR (detection + characterization + graph + artifact + prediction)
- godon-bench-generic 0.1.0 released to GHCR (configurable synthetic bench with ground truth)
- Helm chart for causal (merged)
- Observer proxies detection to causal (coupling-detection endpoint)
- PRs: godon-images #254 (merged), godon-charts #203 (merged), godon-images #255 (merged), godon #269 (open, scenarios), godon-breeders #165 (open, strain)
- Roadmap written and updated at /projects/godon/docs/notes/causal-roadmap.md
- Build spec at /projects/godon-images/godon-causal-build-spec.md

## IMMEDIATE BLOCKERS (in dependency order)

1. Coordinator timing bugs — receiver drops HOLD early, trial gaps under load
2. Causal image untested against real trial data
3. 4-breeder chain composition test — the gate
4. Detection result unpublished (Priority 1 since July 18)
