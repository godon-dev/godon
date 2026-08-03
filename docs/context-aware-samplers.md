# Context-Aware Samplers

A design direction for the godon platform.

## The Problem

Standard optimization samplers (TPE, CMA-ES, grid, random) assume a fixed
problem: static search space, static objectives, static constraints. They
treat each trial as an independent observation in an unchanging landscape.

In reality, multi-breeder optimization is dynamic:

- **Coupling** — one breeder's trials affect another's target
- **Boundary constraints** — the optimal point sits at the edge of the
  configured search space, suggesting the space is wrong
- **Parameter irrelevance** — some parameters barely affect quality, wasting
  search budget
- **Guardrail overcorrection** — constraints block a large fraction of trials,
  distorting the search distribution

These are meta-signals about the optimization process itself. Current samplers
cannot see them.

## The Current Workaround: Detect and Reconfigure

The observer detects meta-signals, alerts the operator, who adjusts the
breeder config and starts a new instance. This works because:

- **Transparent** — the operator sees and approves each change
- **Auditable** — every adjustment is a config diff
- **Composable** — works with any sampler

But it breaks down for continuous optimization (homeorhesis). Pausing and
restarting a breeder loses trajectory information. The reconfiguration loop
is too coarse-grained to track fluctuating coupling strength or drift.

## The Proper Architecture: Context-Aware Sampler

A `ContextAwareSampler` that wraps any base sampler (TPE, CMA-ES, etc.) and
injects external signals into trial suggestions.

```
┌─────────────────────────────────┐
│       ContextAwareSampler       │
│                                 │
│  ┌───────────┐  ┌────────────┐  │
│  │ base      │  │ context    │  │
│  │ sampler   │  │ signals    │  │
│  │ (TPE etc) │  │            │  │
│  └─────┬─────┘  └─────┬──────┘  │
│        │              │         │
│        └──────┬───────┘         │
│               ▼                 │
│        trial suggestion         │
│        (param + context)        │
└─────────────────────────────────┘
```

The sampler accepts a context object each trial:

```python
context = {
    "coupling": {
        "neighbor": "bench-s4-2",
        "strength": 0.47,
        "direction": "incoming",
        "affected_objectives": ["energy", "water"]
    },
    "boundary_proximity": {
        "heating_setpoint_zone1": 0.95,  # near upper bound
        "co2_injection": 0.12            # near lower bound
    },
    "parameter_sensitivity": {
        "irrigation": 0.02,              # barely affects quality
        "light_intensity": 0.78          # strong effect
    },
    "guardrail_pressure": {
        "max_temp": 0.35                 # blocking 35% of trials
    }
}
```

## What the Sampler Does With Context

### Coupling

When incoming coupling is detected on specific objectives, the sampler can:

- **Widen exploration** in the affected parameter subspace (the landscape is
  shifting, don't overfit to a single region)
- **Penalize configurations** that historically amplified coupling effects
- **Bias toward robustness** — suggest parameter sets that are less sensitive
  to ambient perturbation

### Boundary Proximity

When the best-known params sit at search space edges:

- **Expand the search space** for that parameter beyond the configured range
- **Log a recommendation** to the operator: "widening heating_setpoint_zone1
  from [15,35] to [15,45] based on boundary proximity"
- **Shift the search distribution** toward the unconstrained region

### Parameter Sensitivity

When a parameter barely affects quality:

- **Fix the parameter** at its current best value and remove it from the
  search space, reducing dimensionality
- **Reallocate search budget** to high-sensitivity parameters
- **Log a recommendation**: "irrigation has <2% effect on quality, consider
  fixing it"

### Guardrail Pressure

When guardrails block a large fraction of trials:

- **Shift the search distribution** away from the guardrail boundary
- **Log a recommendation**: "max_temp guardrail blocks 35% of trials,
  consider raising from 40 to 42"
- **Track guardrail hit rate** as a convergence signal

## Implementation Path

### Phase 1: Detection Only (Current)

The observer detects and displays meta-signals. The operator reads them and
manually adjusts config. No sampler changes.

### Phase 2: Recommendations

The observer produces actionable config suggestions. The operator approves
them. The controller applies them by restarting the breeder with updated
config.

### Phase 3: Context Injection

The `ContextAwareSampler` wrapper is implemented. It accepts context signals
and adjusts trial suggestions in-flight. The operator still sees what changed
and why, but adaptation happens without restart.

### Phase 4: Autonomous Adaptation

The feedback loop closes: observer detects → controller computes context →
sampler adapts → results feed back to observer. The operator sets goals and
constraints; the platform handles continuous adaptation.

## Design Principles

1. **Wrapper, not replacement** — the context-aware sampler wraps any
   existing sampler. TPE, CMA-ES, random — all work. Context is an overlay,
   not a new algorithm.

2. **Legibility over cleverness** — every adaptation must be explainable.
   "Widened search space because best params were at boundary" not
   "sampler adjusted distribution."

3. **Human in the loop until proven otherwise** — the sampler suggests,
   the operator approves. Full autonomy is earned, not assumed.

4. **Audit trail** — every context signal and its effect on the search
   is logged. The optimization process is reproducible.

## Why This Matters

This is the platform's core differentiator. Any optimization tool can find
the best parameters in a fixed search space. godon can tell you that the
search space is wrong, that your parameters are interfering with each other,
and adapt in-flight. The sampler isn't just searching — it's learning about
the problem it's solving.

The stasis patterns (homeostasis → allostasis → homeorhesis → autopoiesis)
are the trajectory. The context-aware sampler is the mechanism that makes
each transition possible without architecture changes.
