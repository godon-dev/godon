# Forms of Stasis in Optimization Systems

A design vocabulary for composing optimization strategies in godon.

## Overview

Stability in complex systems takes many forms. The godon engine does not
implement any single form of stasis explicitly. Instead, it provides
mechanisms — search algorithms, evaluation, coupling detection, continuous
adaptation — and the configuration of breeders, targets, and observers
determines which form of stability *emerges*.

These patterns are not features to be checked off. They are compositional
building blocks for expressing optimization intent.

## The Patterns

### Homeostasis — Converge to a Fixed Optimum

The system seeks a single stable point and stays there. Each breeder
optimizes independently toward its best-known configuration.

**Configuration**: Single breeder per target, fixed search space, convergence
criteria (min/max iterations, quality threshold).

**Limitation**: The optimum is stale the moment the environment changes.
Coupling, load shifts, or external perturbation degrade performance silently.

### Allostasis — Anticipatory Adjustment

The system adjusts *before* disruption hits, based on observed patterns
from neighboring processes. Not reactive — predictive.

**Configuration**: Coupling detection enabled (cross-examination), breeders
receive neighbor state or interference signals, adjustment logic in the
breeder or controller.

**Emerges when**: Multiple breeders operate on coupled targets (scenario 4).
The cross-examination detection is the first step — you cannot anticipate
what you cannot see.

### Homeorhesis — Stability of Trajectory

The system maintains a stable *adaptation path*, not a fixed point. After
perturbation, it returns to its trajectory, not to a previous state. The
breeder continuously adjusts, and "stable" means the trajectory is
resilient, not that parameters stop changing.

**Configuration**: Continuous mode (no fixed completion criteria), ongoing
evaluation against moving baselines, breeder adapts to environmental drift
over time.

**Emerges when**: Targets have seasonal patterns, load variation, or
gradual degradation. The optimization path itself becomes the output, not
a single best configuration.

### Enantiostasis — Stability Through Opposing Fluctuations

One parameter swings up while another swings down, and the system as a
whole stays balanced. Stability emerges *from* variation, not despite it.

**Configuration**: Multiple breeders on shared targets with opposing
strategies — one optimizes for throughput while another optimizes for
resource efficiency, or one explores while one exploits.

**Emerges when**: Resource-constrained environments where aggressive
optimization in one dimension causes degradation in another. The opposing
pressures keep the system in a productive dynamic equilibrium.

### Heterostasis — Stability Through Diversity

Multiple redundant mechanisms pursue the same outcome. If one fails or
gets stuck, others compensate. Diversity of approach prevents lock-in.

**Configuration**: Multiple breeder types (Bayesian, evolutionary, gradient,
random) on the same target, each with different search strategies and
biases.

**Emerges when**: Complex search spaces with many local optima. No single
algorithm reliably finds the global optimum, but the ensemble coverage
improves overall performance.

### Poikilostasis — Deliberate Variability

The system intentionally maintains internal fluctuation rather than
converging. Keeps the optimization responsive and prevents stagnation
at local optima.

**Configuration**: Exploration noise injection, periodic perturbation of
converged parameters, forced restart of search subspaces, epsilon-greedy
scheduling.

**Emerges when**: Search spaces with deceptive gradients or flat regions.
A homeostatic breeder converges prematurely; a poikilostatic one keeps
exploring and may find better regions.

### Autopoiesis — Self-Producing Stability

The system continuously regenerates itself. Components are constantly
being replaced, yet the system persists. Not just stable — self-sustaining.

**Configuration**: Full feedback loop — breeders optimize, observers detect
patterns, controller adjusts breeder configurations, targets evolve. The
platform operates without external intervention, with each component's
output feeding another's input.

**Emerges when**: Long-running production systems where manual intervention
is impractical. The platform monitors, detects, adapts, and reconfigures
autonomously.

## Progression

These patterns are not alternatives — they build on each other:

```
homeostasis → allostasis → homeorhesis → autopoiesis
                  ↓              ↓
            enantiostasis   poikilostasis
                  ↓
             heterostasis
```

1. A single breeder achieves **homeostasis**.
2. Coupling detection enables **allostasis**.
3. Continuous adaptation produces **homeorhesis**.
4. Multiple strategies compose into **enantiostasis** and **heterostasis**.
5. Exploration noise maintains **poikilostasis**.
6. The full feedback loop closes into **autopoiesis**.

The progression is emergent from real problems. You do not design for
autopoiesis on day one — you solve homeostasis, hit its limits, discover
coupling, solve that, and arrive at more sophisticated forms organically.

## Design Principle

The engine is stasis-agnostic. It provides:

- **Search**: parameter space exploration (Optuna, multiple samplers)
- **Evaluation**: trial execution and quality assessment
- **Observation**: metrics collection and cross-examination
- **Adaptation**: configuration adjustment based on observed state
- **Coordination**: multi-breeder awareness and interference detection

The user composes these mechanisms into the desired form of stability
through configuration. The patterns above serve as a vocabulary for
expressing intent, not as product features.
