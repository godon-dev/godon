# godon causal — roadmap

an instrument for measuring, modeling, and predicting coupling
propagation in complex systems.

## what exists today

**CFAR coupling detection — proven.** two independent optimizers on coupled
non-linear non-stationary systems (greenhouse simulators) discovered their
physical coupling through active probing with CFAR block-step detection.
coupling 0.9 detected bidirectionally. coupling 0.0 clean control — zero
false positives. reproduced across multiple runs.

all previous passive detection methods (FFT, granger, mutual information,
transfer entropy) failed on this channel type at 200-300 trial budgets.
active probing succeeds because it eliminates the dominant noise source
(receiver self-exploration) and creates a signal strong enough to survive
non-linear distortion.

**coordinated detection protocol — functional but not yet clean.** the
breeder detection coordinator implements a state machine: OPTIMIZE ->
HOLD_CALIB -> IMPULSE_CALIB -> PUSH -> PAUSE -> DONE -> COOLDOWN. sender
pushes parameters to extremes, receiver holds at neutral. turn-taking via
DB-backed fencing token lease. known timing issues: receiver may drop out
of HOLD before sender finishes, trial gaps under load.

**godon-causal service — scaffolding, not yet tested against real data.**
Rust service that reads interventional probe trials, runs CFAR detection
(behind a trait — swappable), characterizes edges, builds the coupling
graph, exports as transferable JSON artifact. compiles, ships as container,
CI passes. has never processed real probe data.

## the method

### no human-specified structure

every existing modeling approach embeds human assumptions before the
method starts:

- system identification: human specifies model structure (ARX, state-space)
- DCM: human proposes candidate coupling architectures
- analytical modeling: human writes the equations
- digital twins: human builds the simulation
- RL: human designs reward function and network architecture

all of these are human policies about the system. if the assumption is
wrong, the method fails silently — the model faithfully represents a
system that doesn't match reality.

godon eliminates human-specified structure entirely. no human specifies
the topology. no human specifies the response functions. no human
specifies the model structure. no human specifies the equations. the
system describes itself through measured responses to controlled
intervention.

the ONLY human input is the measurement protocol — push, hold, pause.
that is a procedure, not a policy about the system. it is domain-agnostic:
the same protocol measures greenhouse coupling, data center coupling,
power grid coupling, microservice coupling.

### the role of metaheuristics

metaheuristics are policy-free in Talbi's classification: they adapt
their search based on observations but never produce a persistent,
deployable strategy. the search dynamics (TPE density estimates,
CMA-ES covariance matrices) are consumed by the run and discarded. this
distinguishes them from RL, where the policy IS the product.

currently the breeder uses metaheuristics to optimize the system
objective directly (maximize growth_rate). this is the wrong target.
the metaheuristic should optimize META objectives — information gain
about coupling structure, coverage of the operating space, characterization
quality. the system objective (growth_rate, energy efficiency) is a
byproduct of understanding the system, not the target of the search.

once the coupling graph is measured, the system optimum is computed
analytically from the response functions. the metaheuristic becomes
unnecessary for optimization — it was necessary for exploration and
characterization, not for finding the optimum.

the metaheuristic is the universal sampling engine for every phase
where you need to explore an unknown space without committing to a
model:

1. initial exploration — maximize objective (standard, finds operating region)
2. calibration — minimize objective variance (finds quiet baseline state)
3. characterization — maximize coverage / information (measures response curves)
4. detection — coordinator choreography takes over (push/pause/hold)

### how coupling is measured

the system probes itself. one optimizer pushes parameters to extremes
while all others hold still. the perturbation travels through coupling
channels. the receiver's objective shifts. CFAR block-step detection
compares the shift during push to the shift during pause (reversibility
check). if both exceed the CFAR threshold, coupling is detected.

this is intervention (pearl level 2), not observation (level 1). the
sender was at extremes, the receiver was holding still. the shift IS
the coupling response — no statistical confounding.

the contribution is not limited to hidden coupling. known coupling
that has never been quantified precisely enough to compose into
multi-hop predictions is an equally important target. data center
operators know racks exchange heat. nobody has measured the edge
weights precisely enough to predict what happens three racks away.

### how the graph is built

each detected edge carries:
- which sender, which receiver, which channel (objective or observation)
- coupling strength (sensitivity = response shift / impulse magnitude)
- noise floor (receiver variance during baseline)
- confidence (fraction of probe rounds that detected)
- recovery fraction (how much the receiver returned to baseline during pause)

the full graph is the connectome — a directed graph of measured coupling
between all optimizer pairs.

### how prediction works — forward simulation

naive composition says: edge A->B measured at 0.7, edge B->C at 0.5, so
perturbing A shifts C by 0.35. this is wrong for non-linear systems
because the edges are state-dependent — B's response to A changes when
C is also pulling on B.

the solution is iterative forward simulation — the same numerical method
used in circuit simulators (SPICE), power grid load flow, and weather
models:

1. A perturbs by delta
2. B responds based on its measured response function
3. B's new state changes the B->C coupling — recompute C's response
4. C's response feeds back to B — update B again
5. iterate until convergence

this is not composition of multipliers. it is propagation of a
perturbation through the graph with state updates at each node. the
measured edge weights are local derivatives of the response function
at each operating point.

for accurate iteration, edges need to be characterized at multiple
operating points (baseline, slightly elevated, strongly elevated). the
metaheuristic samples these points; the hold-and-measure protocol gives
clean data at each.

### how the model stays alive — the maintenance loop

the model is predictive, not continuous. you probe to build it, then
operate from the frozen snapshot. the robot downloads it, the controller
embeds it, the LLM reasons from it. nobody probes during operation.

reprobing is triggered by prediction error. the system operates from
the frozen model, compares predicted behavior to actual. when they
diverge, something physically changed — rescan that neighborhood. not
the whole graph. just where the model went stale.

the ratio of scanning to operating adapts to structural volatility.
stable systems need infrequent rescans. volatile systems need frequent
ones. the snapshot degrades gracefully — edges carry timestamps,
confidence widens as the scan ages.

### the artifact

the connectome is a measured model, not a policy. it says "if you push
here, the system responds like this." it does not say "push here." many
different operating policies can be derived from the same connectome.
the connectome carries no human assumptions about the system — it is
purely empirical, discovered through intervention.

the snapshot is:
- empirical (measured through intervention, not derived from equations)
- explicit (a graph with measured weights, not opaque neural weights)
- transferable (a JSON file — robot loads it, LLM queries it, controller
  embeds it)
- temporally stamped (valid for a moment, degrading as system drifts)
- assumption-free (no human-specified structure, model class, or equations)

this is distinct from analytical models (brittle, require a-priori
knowledge), learned models (opaque, non-transferable), and expert systems
(stale, capture design intent not operational reality).

### what it enables

with a measured structural causal model — the response function f for
each node, discovered empirically — all three levels of pearl's ladder
of causation are computable:

- level 1 (association): baseline statistics from the connectome
- level 2 (intervention): forward-simulate — "what happens if I perturb A?"
- level 3 (counterfactual): condition on observation, infer noise, replay
  with different intervention — "given that I observed Y after doing X,
  what would Y have been if I had done Z instead?"

the prediction-error loop validates counterfactuals continuously. every
prediction is implicitly a counterfactual test. the delta corrects the
structural equations where they failed.

## architecture — component separation

the system separates into components, each with a clean identity.
each is replaceable without breaking the others. stackable,
composable, clean interfaces between them. the exact component
count and boundaries are not finalized — the separation itself is
the principle.

### breeder — metaheuristic optimizer

the breeder is a production-grade metaheuristic optimizer. its identity
is optimization, not measurement. it never does coupling work directly.

four roles in the full lifecycle:

1. **simple systems** — no coupling. customer has one target, no
   neighbors. breeder optimizes directly. standard metaheuristic. no
   graph needed, no measurement agent needed. this use case exists today.

2. **bootstrap** — day one on a new coupled deployment. no graph yet.
   customer needs results now. breeder runs, finds good parameters
   immediately. its early optimization trials seed the graph as noisy
   characterization data — not wasted.

3. **graph-guided** — the graph exists and is mature. the breeder's
   metaheuristic evaluates configurations on the graph (microsecond
   evaluations) instead of the real system (minute-scale trials).
   1000x faster optimization on the measured model.

4. **frontier exploration** — the graph covers the characterized
   operating region. customer wants to try a radically different
   parameter regime. graph has no data there. breeder explores
   blindly, extends the frontier. the measurement agent follows to
   measure coupling in the new region.

the breeder integrates with the rest of the engine through three
touchpoints only:

- reads the graph (when available) for warm-start hints and
  graph-simulated evaluations
- yields the system when the measurement agent needs quiet
  (one signal: pause/resume)
- trial data available to the measurement agent as noisy seed data

otherwise the breeder is independent. it optimizes. it always
optimizes. it never measures coupling.

### measurement agent (name undecided)

a purpose-built measurement agent. it does not optimize. it runs
designed experiments: push, hold, measure, sweep.

its heartbeat is not ask-effectuate-reconnoiter-tell (the breeder's
loop). it is push-hold-measure-characterize. the coordinator logic
(lease management, push blocks, pause blocks, calibration) lives here.

it shares infrastructure with the breeder — same targets, same
effectuation, same reconnaissance, same guardrails, same trial
storage. different inner loop, different purpose.

it produces the probe data that causal reads to build the graph. its
output is characterized edges with response functions, not
optimization results.

### causal — computation engine

causal reads probe data, detects coupling edges (CFAR behind a trait),
characterizes them, assembles the graph, exports the artifact, and
computes predictions and optima.

it never probes. it never optimizes the real system. it computes on
the measured model.

### the connectome and the markov blanket

the markov blanket — the statistical boundary where internal states
become independent of external states — is a central concept in active
inference (friston). but it has a fundamental problem for coupled
systems.

statistical independence is not a property of the system. it is a
property of the INSTRUMENT. it holds at the boundary where coupling
drops below the measurement floor. thermal radiation crosses every
wall. ground vibration propagates through foundations. at sufficient
sensitivity there is no true independence — only coupling too weak
to detect.

the CFAR detection threshold IS the practical definition of
statistical independence. "i cannot detect coupling above my noise
floor, so i treat it as independent." the blanket is where the
detector stops finding edges.

this means the blanket is measurement-dependent. it shifts with
sensitivity, noise, probe amplitude, system state. the connectome
does not find THE blanket. it finds the blanket at the current
measurement sensitivity. which is the only blanket that matters —
the one you can act on.

there is also a circularity in friston's blanket for coupled systems:
you cannot define the correct blanket without knowing all coupling
channels. you cannot assume you know all channels because hidden
coupling might exist. you cannot prove statistical independence holds
without exhaustively probing every channel — which is the very
problem you are trying to solve.

the practical alternative: define the boundary by control authority
and measurement coverage, not by statistical independence. what you
control is inside. what you measure crosses the boundary as
structured input with known response functions. what you haven't
measured crosses as unstructured noise. each measured edge turns
unstructured noise into structured input. the connectome is the
process of pushing the practical boundary toward true independence.

### optimization value scales with coupling magnitude

the graph covers all measured edges — local and coupling. but if
coupling contribution is negligible, the optimal configuration
accounting for coupling is approximately the same as ignoring it.
heating=28 either way.

the value of the coupling edges is proportional to how much they
CHANGE the optimum compared to independent optimization. if neighbor
coupling shifts your optimal heating from 28 to 27.8 — negligible.
if it shifts from 28 to 24 — the coupling matters enormously.

that ratio — how much does joint optimization differ from independent
optimization — is the real measure of the method's practical
optimization value. it is empirical. depends on the system, the
coupling strength, the objective landscape.

the composition test should measure this explicitly: compute the
optimum WITH coupling edges and WITHOUT them. if they differ
significantly, the coupling graph changes operational decisions. if
nearly identical, the graph is a more precise way to arrive at the
same answer independent optimization would have found.

this does not make the graph worthless for weak coupling — prediction,
drift detection, transfer, and self-diagnosis of incompleteness still
matter. but the OPTIMIZATION value of coupling edges scales with
coupling magnitude. weak coupling = same answer. strong coupling =
different answer.

the greenhouse bench runs at 0.9 — deliberately strong. what happens
at 0.3? 0.1? where does coupling stop changing the optimum? that is
a sweep for the generic bench.

multi-target pareto optimization on the measured graph is where this
becomes uniquely valuable. two targets with conflicting objectives
connected by a coupling edge — the graph reveals tradeoffs created BY
coupling that independent optimization cannot find. the breeders each
find their individual optimum. both locally optimal, jointly
suboptimal because neither sees the coupling. the causal-graph pareto
frontier finds configurations better for BOTH by accounting for the
edge between them. that frontier cannot exist without measured
coupling — the tradeoffs it reveals are invisible to every method
that does not see the edges.

the first scan of a system is guaranteed to be incomplete. there will
always be coupling channels nobody thought to probe — emergent paths
created by shared physical substrate that no design document specifies
and no expert analysis enumerates.

human intelligence will never fully cover coupling channels upfront
analytically. exhaustive probing is intractable above a few parameters.
expert review finds designed interfaces but misses emergent coupling.
sensitivity analysis only finds edges you thought to test.

the maintenance loop solves this as a side effect of its primary
function. it does not need to know what to look for. it operates the
system, predicts behavior from the graph, compares to reality. the
prediction error IS the discovery signal.

two failure modes, distinguishable from the error pattern:

- **drift** — known edge changed weight. error concentrated on one
  channel after a system change. rescan that edge. fixed.

- **missing edge** — unknown coupling path. persistent error across
  multiple channels, stable over time, correlated with specific
  neighbor activity. the graph does not know about a coupling that
  exists.

localization: if node B's prediction is consistently wrong but only
when neighbor C is active, the missing edge probably involves C to B.
probe the C-B pair specifically. the prediction error narrows the
search from "everything" to "this neighborhood."

the graph diagnoses its own gaps. prediction error reveals what is
missing. targeted probing fills it. the graph converges toward
completeness over time through its own failure signal. this is the
only approach that does not require upfront enumeration of all
coupling channels — which is the one thing nobody can do.

the coordinator timing bugs that exist today come from forcing a
measurement instrument (the coordinator) inside an optimization loop
(the breeder). the coordinator fights the breeder's optimization
rhythm: "stop optimizing, hold still, let me probe." the breeder
resists because optuna wants to sample, not hold.

by separating the measurement agent from the breeder, the conflict
disappears. the measurement agent holds by default — it is not an
optimizer, it does not resist holding. the breeder yields cleanly
when told — it pauses optuna, freezes params, resumes when released.

### the graph as dominant entity

the connectome is the dominant entity wherever it can be measured.
it covers both inter-node coupling edges AND intra-node local response
functions. a parameter with no cross-system coupling still has a
measured response: "heating at 28 produces growth_rate 0.7." that is
an intra-node edge in the graph.

if the measurement agent characterizes both coupling and local
responses, the graph owns the full response surface. the system
optimum is computed analytically from the measured model. no
metaheuristic search needed.

the breeder's remaining role:

1. **frontier exploration** — explore regions the graph hasn't
   measured. extend into new operating regimes. graph follows and
   absorbs the new territory.

2. **bootstrap** — day one, before the graph exists. find the
   operating region. generate initial perturbation data.

the breeder is subordinate to the graph. it serves the graph's
growth, not the customer's objectives directly. the graph serves
the customer. the graph computes the optimum. the breeder explores
so the graph can follow.

coordination between components is complex — scheduling who probes,
who holds, who explores, in what order. this complexity is inherent
to the problem and expected. the component separation makes it
manageable by giving each a clean interface to the others.

### characterization protocol

the current coordinator pushes the top-3 parameters to extremes
simultaneously. this detects coupling but produces a lumped response —
you can't attribute the shift to individual parameters. for accurate
forward simulation, each edge needs a response function measured at
multiple operating points.

the characterization protocol uses the metaheuristic as a sampling
engine: suggest a configuration, hold there for N trials, measure
cleanly, move to the next point. the metaheuristic provides high-D
coverage; the hold provides clean signal. no deterministic grid needed
in high dimensions. no regression needed to decompose confounded data.

### coordinator timing reliability

the receiver may drop out of HOLD before the sender completes a full
push+pause round. trial gaps occur under DB load. these produce missing
receiver data and degrade detection quality. documented, not yet
resolved.

### composition validation

the 4-breeder chain test has not been run. perturb breeder 1, measure
breeder 4 through the chain. does the forward simulation predict the
response? at what coupling strength does iteration diverge from reality?
this is the empirical gate — not theoretical, measured.

### scan scheduling at scale

for N nodes, full pairwise probing is O(N^2). at 4-8 nodes this is
tractable. at 50 nodes it becomes a scheduling problem: who probes,
who holds, in what order, given that probing one pair may require
holding nodes coupled to both endpoints. the connectome helps solve
its own scheduling (skip pairs that showed no coupling), but the
coordinator logic is genuinely new territory.

### handling high-dimensional coupling

the method scales if coupling channels are independent (linear cost
per channel). the wall is interacting parameters — N parameters
that only produce coupling together create an N-dimensional surface.
full grid fitting explodes exponentially.

but real systems have low EFFECTIVE dimensionality even with many
parameters. a 20-parameter coupling surface almost always lives on
a 3-4 dimensional manifold inside that 20D space. most parameters
either don't matter or move together.

the pipeline for high-dimensional coupling:

1. **active probing** — clean perturbation data (input vectors,
   output responses). the measurement agent already produces this.

2. **decomposition** — apply methods that reveal the structure:
   - sequential ablation (knock out one param at a time, see what
     breaks) — O(N) probes to screen N parameters
   - ANCOVA decomposition (split into main effects + pairwise
     interactions + higher-order)
   - active subspace identification (constantine, 2015 — find
     which directions in parameter space explain most variance)
   - sparse regression / compressive sensing (LASSO, basis pursuit)

3. **bundle identification** — the decomposition reveals which
   parameters interact. if A, B, C are statistically inseparable
   (they move together to produce coupling), bundle them. the bundle
   IS the coupling unit. the interaction IS the channel.

4. **characterization** — fit response curves on the identified
   bundles and independent channels. low-dimensional. tractable.

key insight: the lumped push the coordinator already does IS the
bundle measurement. for interacting parameters, the bundle is the
correct unit of characterization — don't decompose it. the
decomposition step tells you WHICH parameters form bundles. the
characterization step measures each bundle as one edge.

the maintenance loop corrects decomposition errors: if prediction
error is high on an edge, re-run decomposition with new data. new
bundles may emerge. the graph self-corrects.

this is borrowed math from genomics (gene knockout), uncertainty
quantification (polynomial chaos), and signal processing (compressive
sensing). the novelty is applying it to coupling characterization
between autonomous systems — which nobody has done because nobody
had the clean interventional data to feed it.

### tractability is always preserved

the high-dimensional interaction problem is real but it does NOT
block the pipeline. characterization degrades gracefully:

1. **detect** (lumped push) — edge exists. proven, reliable.

2. **characterize simple** (one sweep per parameter, others at
   neutral) — N separate 1D curves. always cheap: ~5 points × N
   parameters per edge. assumes independence.

3. **predict** — forward simulate using the 1D curves. compare to
   reality.

4. **if prediction good enough** — done. graph predicts. pareto
   works. counterfactuals compute. no decomposition needed.

5. **if prediction fails** — interactions present. decomposition
   (ablation, ANCOVA, bundles) finds them. re-characterize with
   bundles. predict again.

the worst case degrades to "1D curves with known approximation
error" — not "intractable explosion." the graph always produces
SOMETHING useful. prediction quality scales with characterization
depth. the maintenance loop's prediction error tells you when to go
deeper.

nobody needs to solve the high-dimensional problem upfront. you
tackle it only where and when the cheap approach fails. for most
physical systems with independent coupling channels, the cheap
approach (step 2-4) is sufficient. the expensive machinery (step 5)
is reserved for edges where prediction error demands it.

## immediate next actions (in order)

### 1. fix coordinator timing (blocks everything)

the receiver drops out of HOLD before the sender finishes a full
push+pause round. trial gaps occur under DB load. without clean
rounds, no downstream step produces trustworthy data.

specific work:
- trace coord_state / coord_debug / lease_phase on receiver trials
  during a bench run
- find where receiver exits HOLD prematurely
- ensure receiver holds for entire push+pause+done cycle
- verify no trial gaps under normal load

verification: run greenhouse bench scenario-4 at coupling 0.9.
receiver produces COMPLETE hold trials for every sender round. zero
missing receiver data in detection output.

### 2. test microgrid bench detection (cross-channel validation)

the microgrid bench has never been tested with the detection
coordinator. different coupling physics (approximately linear,
frequency/voltage vs thermal/humidity). same method, untested
parameters.

specific work:
- run scenario-microgrid at coupling 0.9 and coupling 0.0
- check detection output from causal /detect endpoint
- compare to greenhouse results

verification: coupling 0.9 detected, 0.0 not detected. if the
CFAR parameters need tuning for the microgrid timescale, document
what changed.

### 3. debug causal against real data (first connectome)

causal has never processed real trial data. POST /build reads
trials from DB, runs CFAR, builds graph. bugs expected.

specific work:
- run greenhouse bench scenario-4 with working coordinator
- POST /build on causal
- debug: trial reading, phase classification, detection, graph assembly
- compare causal /detect output to observer's detection for same pair

verification: causal produces a graph with edges that match the
observer's detection result. edge weights in plausible range.
artifact export works.

### 4. composition test (the gate)

the single experiment that determines whether the arc holds.

specific work:
- use generic bench with chain4 topology (known ground truth:
  0.7 x 0.5 x 0.3 = 0.105 expected composition)
- OR use 4 greenhouse breeders in a chain topology
- run detection for all pairs
- build graph in causal
- measure each edge independently
- predict end-to-end response from composed edges
- perturb node-1, measure actual response at node-4
- compare prediction to reality

what to measure explicitly:
- does naive composition work? (0.7 x 0.5 x 0.3 = 0.105 vs actual)
- does iterative forward simulation converge? how close?
- compute optimum WITH coupling edges vs WITHOUT — do they differ?
  (the ratio of joint-vs-independent optimization value)
- at what coupling strength does composition break?

verification: publishable result either way. "measured coupling
edges compose to predict multi-hop effects at accuracy X" or
"composition requires iterative simulation, naive multiplication
fails at coupling strength Y."

### 5. shard roles (after composition validated)

separate breeder (optimizer) from measurement agent (designed
experiments) from causal (computation). based on what the
composition test reveals about what the measurement agent actually
needs to do. not before.

## milestones

### milestone 1: reliable multi-pair detection
fix coordinator timing. ensure clean push/pause/hold rounds for all pairs.

### milestone 2: first connectome
deploy godon-causal against live probe data. POST /build produces a graph
with real edges.

### milestone 3: composition validation
4-breeder chain test. perturb breeder 1, measure breeder 4. test naive
composition first. test iterative forward simulation. publish the result
either way.

### milestone 4: characterization protocol
metaheuristic-driven sampling with hold-and-measure. edges carry response
curves, not single derivatives. forward simulation uses curves for
accurate iteration.

### milestone 5: maintenance loop
long-running scan-predict-compare-rescan. prediction error guides
reprobing.

### milestone 6: transfer and accumulation
connectome snapshot as transferable artifact.

## deployment targets

phase A: bench simulators with dedicated push/hold — proven
phase B: bench simulators with watermark-only — partially done
phase C: controlled real infrastructure with probing windows — next
phase D: production infrastructure with embedded probing — goal

## positioning

active inference (Friston) provides the correct loop for coupled systems:
predict -> compare -> update -> act. its bottleneck: it requires an
analytically specified generative model. for complex coupled non-stationary
systems, this specification is intractable.

godon measures the generative model empirically through active probing.
the scan replaces the specification. the rescan replaces the structural
assumption. Friston updates model parameters within fixed structure.
godon updates model structure itself.

this is not competing with Friston. it completes his pipeline. his loop
runs on top of the measured connectome instead of a specified model.

## the bet

bounded downside: composition fails, prediction doesn't work. you still
have the coupling detector — publishable, fundable, deployable on its
own.

transformative upside: composition works. prediction is useful. the
maintenance loop is effective. the snapshot transfers. accumulated graphs
reveal patterns. the instrument class generalizes.

the foundation is proven. the rest is engineering and empirical
validation.
