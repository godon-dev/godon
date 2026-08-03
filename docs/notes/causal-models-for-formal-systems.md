# Causal Models for Formal Systems — Beyond Infrastructure

Internal notes — not published. Captured July 23, 2026 session. Extends
the-artifact-thesis.md to non-infrastructure domains: code, text, and the
model entity that perturbation-based probing produces for formal systems.

The core question: if godon's perturbation principle extends beyond physical
infrastructure to code and text, what model entity results? Is it novel? And
what does it mean for AI?

## The Principle Is Domain-Agnostic

The pipeline does not change across domains. Only the effectors (what you
perturb) and sensors (what you measure) change:

```
Domain          Effector (perturb)        Sensor (measure)         Output
──────────────  ─────────────────────     ───────────────────      ──────────────
Infrastructure  param change (SSH/HTTP)   metrics (Prometheus)     coupling SCM
Code            mutation (edit element)   behavior (test runner)   dependency SCM
Text/Legal      edit (change clause)      effect (LLM judgment)    semantic SCM
```

Same stages: discover topology → characterize edges → compose for prediction
→ maintain through error-driven re-probing. The detection, characterization,
composition, and maintenance layers are domain-agnostic. The investment in
the pipeline transfers. Only the probes swap.

## The Model Entity: NOT an LLM

This is the critical point. A model trained on perturbation-response pairs
for a formal system is a fundamentally different kind of object than an LLM.

### The AI Entity Taxonomy

```
                    Observational training          Interventional training
                    (learns from seeing)             (learns from doing)
                    ───────────────────────          ──────────────────────
Implicit / neural   LLM                              World model (Dreamer)
                    "I learned text patterns"        "I learned what actions do"

Explicit / graph    Knowledge graph                  Structural causal model  ← THIS
                    "I store extracted                "I measured what changing
                     relationships"                   X does to Y"
```

The entity sits in the bottom-right cell: **explicit (graph-structured) +
interventional (trained on do-data)**. That cell is empty at scale for formal
systems. Nobody produces it because the structure-discovery bottleneck
prevented it — you needed to know the causal graph to build the model, and the
graph was what you were trying to discover. Perturbation probing removes that
bottleneck.

### Why It Is Not an LLM

| Property | LLM | godon's causal model (formal domain) |
|---|---|---|
| Training signal | Observational text | Interventional perturbation-response |
| Learns | P(token \| context) | P(response \| do(perturbation)) |
| Epistemic level | Pearl 1 (association) | Pearl 2 (intervention), 3 (counterfactual if f characterized) |
| Representation | Distributed weights | Explicit graph + edge functions |
| Interpretable | No | Yes — read the graph |
| Hallucination risk | High (reasons from patterns) | Low (reasons from measurement) |
| Transferable | Partially | Yes — the graph artifact transfers |

An LLM pattern-matches. A causal model propagates interventions through
measured structure. These are fundamentally different computations producing
fundamentally different claims. The LLM says "I believe X depends on Y based
on patterns." The causal model says "I perturbed X and measured Y's response:
it changed by Z, through path P." The first is association. The second is
causation. Pearl's hierarchy separates them for a reason.

### The Property Combination — Why godon's Model Is the Only One

Each property exists in some model type for formal systems. The combination
does not:

```
                        Explicit   Causal   Empirically   Maintained  Transferable
                                   (not      discovered    (living)    (artifact)
                                  correlational)
Analytical model            ✓         ✓          ✗            ✗          partial
  (design docs, specs)
LLM (code/text reasoning)   ✗         ✗          ✗         partial        ✗
Knowledge graph             ✓         ✗          ✗            ✗            ✓
  (GraphRAG, Neo4j+LangChain)
Code property graph         ✓         ✗          ✗            ✗          partial
  (Joern, Semgrep, call graphs)
Static dependency graph     ✓         ✗          ✗            ✗          partial
  (imports, calls, types)
Standard SCM (Pearl)        ✓         ✓          ✗            ✗            ✗
godon's formal model        ✓         ✓          ✓            ✓            ✓
```

No existing formal-system model has all five properties. The intersection is
empty until you can discover structure empirically through perturbation —
which is the bottleneck godon removes. Without all five, you have a partial
tool. With all five, you have a new category of knowledge artifact:

- **Explicit + causal** → you can read the dependency graph and query
  interventions ("if I change X, what breaks?")
- **+ empirically discovered** → applicable to systems where the coupling
  isn't declared anywhere (emergent code coupling, semantic text coupling)
- **+ maintained** → stays valid as the codebase evolves, the legal landscape
  shifts, the system drifts
- **+ transferable** → the model is a product. One codebase's causal model
  informs similar codebases. One regulatory corpus's coupling model transfers
  to similar jurisdictions.

This is the same property gap as infrastructure (see the-artifact-thesis.md),
but for formal systems. The bottom-right cell is empty for code and text too.
Nobody has an empirically-discovered, causal, explicit, maintained,
transferable model of a codebase's emergent dependencies or a legal corpus's
implicit semantic coupling. Producing the first one is the invention — and
godon is the only project that has built the pipeline to produce it.

## Application to Code

### Two Layers of Coupling — Opposite Value

**Declared coupling** (imports, calls, type dependencies, inheritance):
already visible. An LLM reading the source sees it. Static analysis traces
it. Perturbation here rediscovers what is on the page. Marginal value.

**Emergent coupling** (hidden, undeclared, runtime):
- "Change this constant from 0.01 to 0.1 — which tests break?" The tests
  that fail are not declared as depending on that constant. The dependency
  emerges through runtime behavior.
- "Change this API's pagination behavior — which services' retry logic
  breaks?" Cross-service coupling through implicit assumptions nobody wrote
  down.
- "Remove this log line — does anything break?" Side effects through implicit
  contracts.

Nobody sees emergent coupling by reading code. Static analysis cannot find
it (not in the type system). Mutation testing touches the primitive ("change
a line, see which tests fail") but uses it for test-quality scoring, not for
building a causal graph.

**Systematizing mutation testing into a causal dependency graph is novel.**
The graph captures: "perturbing function X causes failures in functions Y, Z,
W through paths that are NOT declared as dependencies." That is emergent
runtime coupling — the formal-domain analog of hidden thermal coupling in a
data center. Same epistemological gap. Same probing solution.

### The Architecture Maps

```
Infrastructure godon          Code godon
─────────────────             ─────────────────
breeder (SSH/HTTP)     →      mutation engine (edit code element)
reconnaissance (Prometheus) → test runner / behavioral oracle
observer (coupling detector)→ dependency detector (which changes cause which failures)
controller (coordination)   → sweep scheduler (which elements to mutate, in what order)
```

Mutation testing infrastructure (Stryker, Mutmut, PIT) already exists as the
effector primitive. The detection/characterization/composition layers from
infrastructure godon are reused. The engineering is in the integration, not
in inventing new primitives.

### What the Code Causal Model Enables

- **Impact prediction**: "if I change function X, here are the N downstream
  effects, measured, not guessed"
- **Hidden dependency discovery**: "you didn't declare a dependency between
  service A and B, but perturbing A's config shifts B's latency by 15%"
- **Refactoring safety**: "this change is safe — perturbation confirms zero
  downstream effects beyond the declared callers"
- **Test gap analysis**: "these 5 functions have emergent coupling but no
  tests covering the coupling path"
- **LLM grounding**: an LLM editing code can query the causal model to
  verify its predictions against measured intervention effects

## Application to Text (Legal, Regulatory, Specifications)

### Why Text Has the Most Hidden Coupling in the Formal Domain

Text has less explicit structure than code. No imports, no type signatures,
no function calls. The coupling between clauses is semantic and implicit:

> "Changing the definition of 'force majeure' in clause 7 makes the
> liability cap in clause 143 unenforceable through a chain of
> cross-references and legal logic that nobody wrote as a dependency."

This coupling is genuinely hidden. No extraction tool finds it (it is not a
reference — it is an emergent legal effect). An LLM reading the contract
might catch some, but not systematically, and not reliably across 10,000
contracts.

Perturbation discovers it: change clause 7, systematically check which other
clauses' interpretation shifts, build the causal graph. The graph captures
implicit legal dependencies that emerge from the INTERACTION of clauses, not
from any single clause.

### The Bootstrapping Challenge

For text, the "sensor" (measuring the effect of a textual perturbation)
requires semantic judgment. You need an LLM or legal expert to assess "did
clause 143's meaning change when I modified clause 7?" So you use an LLM to
measure effects that you will feed to an LLM as grounding.

This is not circular if the measurement-LLM and the reasoning-LLM are
different agents. The measurement-LLM answers bounded questions ("does X
change when Y is modified?"). The reasoning-LLM uses the resulting causal
graph to answer open questions. The measurement is structured and repeated;
the reasoning is open-ended. Different tasks, different reliability profiles.

But it is harder than measuring a temperature. The sensor quality limits the
model quality. This is the engineering challenge for the text domain.

### Cross-Document Coupling at Scale

At corpus scale (100,000 contracts, regulatory landscapes spanning
jurisdictions): no LLM holds it all. No extraction tool finds cross-document
hidden coupling. The explicit graph is huge but incomplete — it misses
causal dependencies that emerge from the INTERACTION of documents, not from
any single document.

Perturbation discovers cross-document coupling that no extraction method can
find. "Perturbing clause 7's definition of 'force majeure' makes clause 143
in a DIFFERENT contract unenforceable through a shared regulatory framework."
Nobody wrote that dependency. It emerges from the interaction. Only
intervention reveals it.

## Giving LLMs Causal Understanding

### The Current Limitation

LLMs are trained on observational data (text). They learn associations.
They cannot distinguish "X causes Y" from "X and Y co-occur" from their
training data. This is Pearl's level 1 (association). They are
constitutionally stuck there because their training signal is observational.

### What Perturbation Grounding Provides

A perturbation-derived causal graph provides **interventional evidence**
(Pearl level 2). "I perturbed X and measured Y's response." This is
empirically validated causation, not pattern-matched association.

An LLM grounded in a perturbation-derived causal graph reasons from measured
causation. It cannot hallucinate the coupling because it did not infer it —
it queried it. When its prediction (from the graph) fails against measured
response, the failure is a diagnostic signal, not a hallucination.

### The Neuro-Symbolic Architecture

The LLM and the causal model are complementary layers:

```
Human: "If I change this function, what breaks?"
  ↓
LLM: translates → graph query (which downstream nodes? what response functions?)
  ↓
Causal model: computes f_downstream(f_changed(Δ)) → "3 callers break, errors X, Y, Z"
  ↓
LLM: translates result → "Changing this function would break 3 callers:
      service A (timeout), service B (null pointer), service C (data loss)"
  ↓
Human: receives grounded, measured answer
```

The LLM does language. The causal model does causation. Neither replaces the
other. This is neuro-symbolic: neural language interface + symbolic causal
engine. The neural part handles ambiguity and natural language. The symbolic
part handles exact causal computation grounded in measurement.

## The Deeper Play: Causal Training Signal

Beyond feeding causal graphs to LLMs as context, there is a more fundamental
possibility.

If you accumulate perturbation-response pairs across many codebases or text
corpora, you have a **different training signal** than next-token prediction:

```
Current LLM training:  "given this text, predict the next token"     (association)
Causal training:       "given this perturbation, predict the response" (intervention)
```

Models trained on perturbation-response pairs learn causal dependency, not
co-occurrence. This is Pearl level 2 as a TRAINING OBJECTIVE, not just as a
grounding context.

The entity trained this way is NOT an LLM. It does not predict tokens. It
predicts the causal consequences of interventions. It is a causal world model
— but explicitly structured (graph + functions) rather than implicitly neural.

Whether this works is an open research question. But the training signal is
genuinely different from anything current LLMs learn from. And the
perturbation data is cheap to generate for code (run the tests) and
characterizable for text (LLM-judged effects). The bottleneck is not data
generation — it is the framework for training on interventional rather than
observational data.

## The Value Spectrum: Where the Principle Matters Most

The value of perturbation-based causal discovery is proportional to how
HIDDEN the coupling is:

```
Physical domain (infrastructure, hardware, grids):
  Coupling: hidden, non-symbolic, implicit, noisy
  Existing tools: nothing works at scale
  Value: TRANSFORMATIVE. No alternative exists.

Code — declared coupling (imports, calls):
  Coupling: visible, symbolic, explicit
  Existing tools: LLMs, static analysis — adequate
  Value: marginal. LLMs already see it.

Code — emergent coupling (runtime, undeclared):
  Coupling: hidden, behavioral, implicit
  Existing tools: mutation testing (primitive, unsystematized)
  Value: SIGNIFICANT. No tool discovers this as a causal graph.

Text (legal, regulatory, specs):
  Coupling: hidden, semantic, implicit
  Existing tools: knowledge graphs + LLMs (extract explicit only)
  Value: SIGNIFICANT. No tool discovers implicit semantic coupling.

Cross-document at corpus scale:
  Coupling: invisible across documents
  Existing tools: nothing
  Value: HIGH. The interaction of documents creates coupling nobody can find.
```

The principle is universal. The value is not. It concentrates where coupling
is hidden — which for formal systems means emergent (code) and semantic
(text), not declared (code).

## What Is Novel — The Precise Claim

**CAN claim:**
- "A pipeline that discovers emergent coupling in code through systematic
  perturbation, producing a causal dependency graph that static analysis and
  LLMs cannot derive from reading the source"
- "Empirically-discovered semantic coupling models for legal/regulatory text,
  capturing implicit cross-clause dependencies that no extraction tool finds"
- "A new category of model for formal systems: explicitly-structured,
  interventionally-grounded causal models that move AI from associational
  reasoning (Pearl 1) to interventional reasoning (Pearl 2)"
- "A training signal fundamentally different from next-token prediction:
  perturbation-response pairs that teach causal dependency, not co-occurrence"

**CANNOT claim:**
- "We invented mutation testing" (existing field)
- "We invented causal reasoning for AI" (Pearl)
- "We invented knowledge graphs" (existing)
- "We invented LLMs" (obviously not)

**The novelty is**: producing causal models of formal systems through
perturbation — an entity that does not exist today. Nobody has a causal
dependency graph of a codebase discovered through systematic mutation. Nobody
has a semantic coupling model of a legal corpus discovered through systematic
clause perturbation. The model category (explicit + interventional for
formal systems) is empty. Producing the first instance is the invention.

## Why This Is godon's to Build — The Requirements Gap

Building causal models of formal systems through perturbation requires eight
integrated capabilities. No existing tool, project, or research group has all
eight. godon is the only one that has built (or designed) them as an
integrated system. This is not a minor advantage — it is the reason the model
category is empty and stays empty until someone does the integration work.

### The Eight Requirements

1. **Perturbation engine** — systematically modify elements of the target
   system (mutate code, edit clauses, push params)
2. **Coordination protocol** — control who changes and who holds, to isolate
   causal effects across interacting elements
3. **Measurement/sensing** — measure the system's response to each
   perturbation
4. **Detection algorithm** — statistically detect coupling from
   perturbation-response data
5. **Characterization** — sweep parameters to fit response functions per
   discovered edge
6. **Composition** — combine characterized edges into multi-hop predictions
7. **Maintenance** — prediction-error-driven refresh as the system drifts
8. **Transfer/export** — export the model as a shareable, queryable artifact

### Who Has What

```
                      1     2     3     4     5     6     7     8
                      Pertb Coord Meas  Detct Char  Comp  Maint Xfer
───────────────────  ────  ────  ────  ────  ────  ────  ────  ────
Mutation testing       ✓     ✗     ✓     ✗     ✗     ✗     ✗     ✗
LLMs                   ✗     ✗     ✗     ✗     ✗     ✗     ✗   partial
Static analysis        ✗     ✗     ✓     ✗     ✗     ✗     ✗   partial
Knowledge graphs       ✗     ✗     ✗     ✗     ✗     ✗     ✗     ✓
World models          ✓*    ✗     ✓    partial ✗     ✗     ✗     ✗
Causal discovery       ✗     ✗     ✗     ✓   partial ✓     ✗     ✗
  (academic)
System identification  ✓     ✗     ✓     ✗     ✓     ✗     ✗     ✗
───────────────────  ────  ────  ────  ────  ────  ────  ────  ────
godon                  ✓     ✓     ✓     ✓   designed designed designed ✓

  * world models perturb through the agent's own actions, not systematic
    probing of arbitrary system elements
```

Every other approach has 2-3 of the 8 requirements. godon has 5 built and 3
designed. Nobody else is close to all 8.

### Why Nobody Else Has All Eight

The requirements span fields that do not talk to each other:

- Perturbation + measurement → **software engineering** (testing, mutation testing)
- Coordination → **distributed systems** (consensus, turn-taking, fencing tokens)
- Detection → **signal processing** (CFAR, stacking, radar/seismology)
- Characterization → **control theory** (system identification, Ljung)
- Composition → **statistics / causal inference** (graphical models, Pearl)
- Maintenance → **machine learning** (active learning, prediction-error loops)
- Transfer/export → **data engineering** (artifact formats, versioning)

No single field has reason to integrate all of these. A testing tool does not
need a causal inference framework. A causal inference researcher does not
build mutation engines. A signal processing expert does not coordinate
distributed agents on live infrastructure. The integration is non-obvious
from within any single field — it is only obvious once you frame the problem
as "build causal models of coupled systems through active probing" and follow
the solution wherever it leads.

This is why the cell is empty. Not because the idea is hard to conceive, but
because executing it requires crossing field boundaries that nobody has
incentive to cross. godon crossed them because it started from a concrete
problem (infrastructure coupling) and followed the solution through signal
processing, causal inference, system identification, and multi-agent
coordination — accumulating capabilities that no single-field project would
assemble.

### The Moat Is Integration, Not Invention

All eight capabilities are public knowledge. Any single technique can be
learned from a textbook. The moat is not any one of them — it is having them
all in one system, integrated, tested against real coupled systems.

Scooping godon requires not one insight but eight integrations across seven
fields. Each integration surface has its own learning curve. The detection
method alone took months of iteration (failed FFT/Rayleigh/Granger/transfer
entropy approaches before impulse stacking worked). The coordination protocol
went through advisory locks, fencing tokens, and forced turn-taking before
becoming reliable. Each of these dead ends is institutional knowledge that
does not exist in any paper or textbook — it lives in the commit history and
the session notes.

A competitor who reads this document and understands the principle still
faces months of integration work to replicate what godon has already built.
That is a time-based moat, not a permanent one — but it is real, and it
widens with every additional capability godon adds (characterization,
composition, maintenance).

### The Keystone Closes the Gap

Requirements 5-7 (characterization, composition, maintenance) are designed
but not yet proven. The keystone experiment (composition — do measured edges
predict multi-hop responses?) validates requirement 6. If it works,
characterization (#5) and maintenance (#7) follow as engineering. At that
point godon has all 8, validated, integrated. Nobody else is close.

Until then: 5 of 8 built, 3 designed, still more than anyone else — but the
predictive capability (composition) is the one that converts the system from
a detector into a model-builder. It is the difference between "finds coupling"
and "produces causal models." Run it.

### For Formal Systems Specifically

The infrastructure pipeline is the reference implementation of the
domain-agnostic principle. For code and text, requirements #2-#8 transfer
directly. Only #1 (perturbation engine) and #3 (sensor) change:

- **Code**: #1 = mutation engine (Stryker/Mutmut/PIT exist as primitives),
  #3 = test runner / behavioral oracle
- **Text**: #1 = edit engine, #3 = LLM judgment (bootstrapping challenge)

The investment in coordination, detection, characterization, composition,
maintenance, and export — six of eight requirements — transfers unchanged.
godon is not starting from scratch for formal systems. It is reusing
two-thirds of the pipeline and swapping the probes.

## The Strategic Implication

For infrastructure, the artifact thesis (companion document) applies: build
the first characterized SCM of a real coupled system, publish it, define the
category.

For formal systems, the path is different but parallel:

1. **Start with code, not text.** Code has cheaper sensors (test runners are
   deterministic; LLM judgment for text is noisier). The emergent-coupling
   discovery via systematic mutation is the clearest near-term win. Mutation
   testing infrastructure exists as the effector.

2. **The first artifact: a causal dependency graph of a real codebase.**
   "Here is the emergent coupling structure of [a real open-source project],
   discovered through systematic perturbation, validated against held-out
   mutations. X% of dependencies were undeclared — invisible to static
   analysis." That artifact demonstrates the category.

3. **Feed it to an LLM.** Show that an LLM grounded in the causal graph
   produces more reliable code-change predictions than an LLM reasoning from
   source alone. The comparison is the proof that interventional grounding
   beats observational reasoning.

4. **Then text.** Harder (sensor quality), but higher hidden-coupling
   density. Legal/regulatory is where no alternative exists at all.

5. **Then the training signal.** If perturbation-response pairs become a
   viable training signal, the entity trained on them is the causal world
   model — not an LLM, not a knowledge graph, something new. This is the
   deepest play and the most speculative. But it is the path to AI that
   reasons causally by construction, not by approximation.

## The Relationship to the Infrastructure Work

The infrastructure pipeline (godon's current system) is the PROVING GROUND
for the principle. Physical systems have clean sensors (you measure a
temperature, not a judgment). If the pipeline works there — discover,
characterize, compose, maintain — the same pipeline applies to code and text
with different probes.

The investment in the detection/characterization/composition/maintenance
layers transfers. The code and text applications reuse the core pipeline.
Only the effectors and sensors change. This is why building the
infrastructure pipeline correctly matters beyond infrastructure — it is the
reference implementation of a domain-agnostic principle.

## Summary

The perturbation principle extends beyond infrastructure to any perturbable
system. For code, it discovers emergent runtime coupling that no static tool
sees. For text, it discovers semantic coupling that no extraction tool finds.
The resulting entity is a structural causal model — not an LLM, not a
knowledge graph, but an explicitly-structured, interventionally-grounded
causal model that occupies an empty cell in the AI landscape.

This entity gives LLMs what they constitutionally lack: interventional
grounding (Pearl level 2). An LLM querying a causal model reasons from
measured causation, not from pattern-matched association. And if
perturbation-response pairs become a training signal, the entity trained on
them learns causal dependency directly — a fundamentally different training
objective than next-token prediction.

The invention is the model category for formal systems: causal models built
from perturbation, not from reading. Nobody produces this today. The first
instance — a causal dependency graph of a real codebase — is the artifact
that proves the category.
