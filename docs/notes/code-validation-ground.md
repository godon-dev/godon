# Code as Validation Ground — Engine Architecture

Internal notes — not published. Captured July 23, 2026 session.

## Why Code Is the Right Validation Domain First

Code is the domain where the artifact thesis can be proven fastest and most
definitively, because the substrate eliminates every hard problem from the
infrastructure case:

| Challenge | Infrastructure | Code |
|---|---|---|
| Detection signal | Weak (SNR ~0.002), needs CFAR | Binary (test pass/fail) |
| Noise | Physical noise, exploration noise | None (deterministic) |
| Composition | Keystone — unproven for nonlinear | **Exact** (deterministic function composition) |
| Non-stationarity | System drifts | Controlled (CI runs on fixed versions) |
| Coordination | Turn-taking, lease tables | Not needed (single system) |
| Measurement | Minutes (thermal settling) | Seconds (run tests) |
| Tools | Custom-built | Mutation testing tools exist (Stryker, Mutmut, PIT) |

The keystone — the one thing that's been uncertain throughout this entire
analysis — **is trivially true for code.** Composition of deterministic
functions is exact. No approximation. No error bounds needed. The prediction
`f_Z(f_Y(f_X(Δ)))` equals the measured response exactly, because code is a
deterministic function and function composition is always valid.

This means: **code is where the artifact goes from "probably possible" to
"definitely possible, exact, and demonstrable in weeks."**

## Reuse the Existing Engine — New Adapters, Not a New System

CORRECTION from earlier framing: you do NOT need a new engine. The existing
godon breeder engine is the RIGHT tool. You need new ADAPTERS (strain +
effectuator + reconnaissance) for the engine you already have. The
optimization-driven loop is exactly right, because you need metaheuristics
(Optuna) to efficiently explore the mutation space rather than mutating
everything exhaustively.

### Why the existing engine is correct for code

Exhaustive mutation testing is O(elements × mutation_types × magnitudes).
For a large codebase, that is millions of mutations — too expensive. You need
INTELLIGENT SELECTION of which mutations to try. That is metaheuristic search.
That is Optuna. The breeder engine already has it.

The loop for code is the SAME loop as infrastructure, with different adapters:

```
Infrastructure loop:                        Code loop:
─────────────────────                       ──────────
ask Optuna → which params to try            ask Optuna → which element+magnitude to mutate
suggest → strain translates to params       suggest → code strain translates to mutation spec
effectuate → SSH/sysctl to live host        effectuate → apply mutation to source
reconnoiter → Prometheus metrics            reconnoiter → run tests, capture outcomes
tell → record objective values              tell → record which tests changed + by how much
repeat                                      repeat
```

Same engine. Same Optuna ask/tell. Same Windmill orchestration. Same
guardrails. Same strain system. Same worker cooperation. Same observer
dashboard. Only the adapters change.

### What is reused (everything you do not want to recreate)

- **Optuna ask/tell loop** — the metaheuristic search. Efficiently selects
  which mutations to try based on what has been learned. TPE/NSGA-II guides
  exploration toward informative mutations. No exhaustive sweep needed.
- **Strain system** — a code strain plugs in exactly like linux_performance,
  bench_greenhouse, bench_microgrid. Same contract: suggest_params + validate_config.
- **Effectuation framework** — a code effectuator plugs in alongside SSH/HTTP.
  Same interface: (context, targets, settings) → summary.
- **Reconnaissance framework** — a test-runner reconnaissance plugs in
  alongside Prometheus/HTTP. Same interface: (context, targets, settings) → metrics.
- **Guardrails** — prevent destructive mutations (don't delete files, don't
  mutate security-critical code). Same guardrail system.
- **Breeder worker lifecycle** — the worker loop is generic. Runs unchanged.
- **Windmill orchestration** — runs code-perturbation workers just like
  infrastructure workers. No new orchestration needed.
- **Worker cooperation** — multiple breeders can explore different modules of
  a large codebase, sharing findings. Same cooperation mechanism.
- **Observer/dashboard** — visualizes the coupling discovery. Same dashboard.
- **MCP/API** — query interface. Same protocol.

### What is new (just adapters)

1. **Code strain** (~200 lines, like bench_greenhouse):

```python
# strains/code_mutation/strain.py
def suggest_params(trial, settings):
    element = trial.suggest_categorical('element', settings['code_elements'])
    mutation_type = trial.suggest_categorical('mutation_type',
        ['change_constant', 'modify_operator', 'remove_statement', ...])
    magnitude = trial.suggest_float('magnitude', 0.0, 1.0)
    return {'element': element, 'mutation_type': mutation_type, 'magnitude': magnitude}

def validate_config(config):
    # Verify code_elements exist, test command configured, etc.
    ...
```

The parameter_registry would enumerate code elements (functions, constants,
config values) discoverable via AST parsing or tree-sitter. Like
linux_performance's 1608-line sysctl registry, but for code elements.

2. **Code effectuator** (~100 lines, like effectuation/http.py):

```python
# effectuation/code.py
def main(context, targets, settings):
    # Apply mutation to source code at targets[0]
    mutation = apply_mutation(targets[0]['path'], settings)
    return {'applied': True, 'mutation': mutation, 'original': mutation.original}
```

3. **Test-runner reconnaissance** (~150 lines, like reconnaissance/http.py):

```python
# reconnaissance/testrunner.py
def main(context, targets, settings):
    results = run_test_suite(targets[0])
    return {
        'tests_passed': results.passed_count,
        'tests_failed': results.failed_count,
        'failed_test_ids': results.failed_ids,
        'output_diffs': results.output_diffs,  # how much each test's output changed
    }
```

4. **godon-causal upper layer** (shared, NEW) — reads the Optuna trial history
   (which mutations affected which tests, at what magnitude) and builds the
   causal graph + response functions + composition + artifact + query. This is
   the domain-agnostic layer that sits on top of the breeder engine's trial
   data. It is the same for infrastructure and code — it reads trial outcomes
   and produces causal models.

### What is NOT needed for code (but harmless if present)

- CFAR/signal processing (detection is binary — test pass/fail)
- Turn-taking/coordination (single system; unless multi-repo exploration)
- Watermarking (no interference between code systems — yet)
- Thermal/power metrics (code has test outcomes)

These are in the existing engine but simply are not exercised by the code
strain. No code changes needed — they are conditionally activated based on
strain/run configuration.

## Architecture: Strain-Based, Not Separate Engine

```
                    ┌──────────────────────────────────────────┐
                    │  godon-causal (NEW shared upper layer)    │
                    │  ├── causal graph builder (from trials)   │
                    │  ├── edge characterization (fit f)        │
                    │  ├── composition (predict multi-hop)      │
                    │  ├── artifact (export/import graph+fns)   │
                    │  ├── query (what_if, impact_predict)      │
                    │  └── mcp interface (for LLMs)             │
                    └──────────────┬───────────────────────────┘
                                   │ reads trial history from
                                   │
          ┌────────────────────────▼────────────────────────────┐
          │  EXISTING godon breeder engine (REUSED, unchanged)    │
          │  ├── Optuna ask/tell (metaheuristic search)           │
          │  ├── breeder_worker.py (lifecycle, guardrails)        │
          │  ├── strain_loader.py (pluggable strains)             │
          │  ├── communication.py (worker cooperation)            │
          │  ├── Windmill orchestration                           │
          │  └── observer/dashboard                               │
          └──────┬──────────────┬──────────────┬─────────────────┘
                 │              │              │
     ┌───────────▼──┐  ┌───────▼───────┐  ┌──▼──────────────┐
     │ infra strain │  │ code strain   │  │ text strain     │
     │ + SSH eff    │  │ + code eff    │  │ + edit eff      │
     │ + Prom recon │  │ + test recon  │  │ + LLM recon     │
     │ linux_perf   │  │ code_mutation │  │ text_coupling   │
     │ greenhouse   │  │ (NEW)         │  │ (future)        │
     │ microgrid    │  │               │  │                 │
     └──────────────┘  └───────────────┘  └─────────────────┘
```

The code strain is just another strain. Like greenhouse or microgrid. The
engine does not know or care that the target is code rather than a greenhouse.
It asks Optuna, gets a mutation spec, effectuates it, reconnoiters tests,
records the outcome. Same loop. Same engine. New adapter.

## Why This Sequence Makes Sense

1. **Code proves the artifact thesis definitively.** Exact composition.
   Clean detection. Fast iteration. The keystone is trivially true. If the
   artifact can't be built for code, it can't be built for anything. If it
   CAN (and it can), the category is demonstrated.

2. **Code validates the shared upper layers.** The composition engine, the
   artifact format, the LLM query interface — these are domain-agnostic.
   Building and validating them for code means they're ready for
   infrastructure and text without rework.

3. **Code has the most immediate consumer.** LLM code editors (Cursor, Claude
   Code, Copilot) are the audience. "An LLM that queries a causal dependency
   model before editing" is a product that exists in a market that exists.

4. **Code is the cheapest to build.** No distributed systems. No signal
   processing. No K8s. No Windmill. A standalone tool that runs as a CLI or
   CI step. Weeks to prototype, not months.

5. **The infrastructure work continues in parallel.** The infrastructure
   pipeline (breeders, observer, coordination) is harder and takes longer.
   Code validation doesn't block it — it runs ahead, validates the upper
   layers, and feeds back the composition engine for infrastructure to reuse.

## What This Means for Architecture

godon should NOT split into separate engines per domain. It should use the
strain system it already has:

- **godon-causal** (NEW, shared upper layer): reads trial history from ANY
  breeder study, builds causal graph + response functions + composition +
  artifact + query + MCP. Domain-agnostic. Sits on top of Optuna trial data.
- **godon-breeders** (existing): the engine. Optuna ask/tell, worker
  lifecycle, strains, effectuation, reconnaissance, guardrails, cooperation.
  Unchanged. Just gets a new strain.
- **code_mutation strain** (NEW, ~500 lines): suggest_params for mutations,
  parameter_registry of code elements, validate_config, preflight. Like
  bench_greenhouse but for code.
- **effectuation/code.py** (NEW, ~100 lines): apply mutations to source.
- **reconnaissance/testrunner.py** (NEW, ~150 lines): run tests, capture
  outcomes + diffs.

Total new code: ~750 lines of adapters + the godon-causal upper layer. The
engine is reused. The metaheuristics are reused. The orchestration is reused.
The guardrails are reused.

## The Verification Plan

Build in this order:

1. **Code strain + adapters** (1-2 weeks). Write the strain, effectuator,
   and reconnaissance. Test against a small codebase. The breeder mutates
   code elements, runs tests, records outcomes. This is the infrastructure
   you do not want to recreate — it already exists.

2. **Run guided mutation exploration** (days). Configure a breeder with the
   code strain on a real codebase. Optuna intelligently selects which
   mutations to try (metaheuristic, not exhaustive). Trial history accumulates
   in the Optuna study DB. Same as any infrastructure optimization campaign.

3. **Build godon-causal graph layer** (1-2 weeks). Read the trial history.
   Build the causal adjacency graph from the mutation-test outcome matrix.
   This is what CPDA does — replicate the causal structure discovery on top
   of godon's trial data.

4. **Characterize edges** (days). For detected coupling edges, configure the
   breeder to sweep mutation magnitude on those specific elements. Optuna
   guides the sweep. Fit response functions per edge. Deterministic, exact.

5. **Compose and validate** (days). Pick a chain A→B→C→D in the graph.
   Predict D's response via composition. Measure D's actual response.
   **They match exactly.** The keystone is proven — in the easiest domain.

6. **Export artifact + LLM grounding demo** (1-2 weeks). Serialize graph +
   functions. MCP interface. An LLM queries the artifact before editing.
   Compare grounded vs ungrounded.

**Total: 4-8 weeks.** Most of the infrastructure already exists. The new work
is three adapters (~750 lines) + the godon-causal upper layer (the shared
composition/artifact/query library, which is also reusable for infrastructure).
