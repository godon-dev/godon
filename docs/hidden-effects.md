# Hidden Effects in Continuous Optimization

Effects that corrupt the optimization landscape beyond the breeder's awareness.
Ordered by severity / likelihood of impact.

## 1. Interference (Cross-Breeder)

Breeders on shared infrastructure unknowingly affect each other's targets.

- Shared compute, network, power, cooling, data stores, API rate limits
- The breeder attributes metric changes to its own parameters, not the neighbor's actions
- Detection: passive statistical methods (Granger, transfer entropy, CCM) on paired trial traces
- Mitigation: detection → isolation, compensation, or coordination
- Status: **planned** — greenhouse bench scenarios 3 vs 4

## 2. Delay / Latency

The breeder measures the previous trial's effect, not the current one.

- Every real system has response latency between effectuation and measurable outcome
- Causes systematic bias — every parameter→metric relationship is shifted in time
- Partially addressed: `stabilization_seconds`, sequential execution, sampling, aggregation
- Remaining risk: fixed stabilization is a guess, may be too short or too long
- Possible improvement: adaptive stabilization (measure until variance drops)

## 3. Hysteresis

Same parameters produce different outcomes depending on the path taken.

- Systems with state: caches, databases, thermal mass, warm-up curves
- The breeder assumes the landscape is stationary at each parameter setting
- Not addressed
- Likely matters for: databases, caches, anything with warm-up
- Mitigation: repeated trials at same parameters, track path-dependency

## 4. Accumulation

Individual trials look harmless but effects compound over time.

- Memory leaks, disk fill, connection pool exhaustion, log bloat
- Breeder sees declining performance, thinks it's doing something wrong
- Partially addressed: guardrail hard limits catch extreme cases
- Not addressed: breeder doesn't know it's causing the degradation
- Mitigation: baseline guardrails, resource monitoring as canary metrics

## 5. Saturation

Pushing a parameter beyond the point where it produces additional effect.

- Diminishing returns: light_intensity above 800, heating past thermal capacity
- Not dangerous, just wasteful — breeder explores dead zones with no signal
- Partially addressed: guardrail hard limits
- Possible improvement: detect flat response regions, deprioritize exploration there

## 6. Shadow Parameters

Hidden state the breeder can't see or control.

- Time of day, queue depth, GC pressure, shared cache state, other services' load
- Breeder attributes metric changes to its parameters when driven by invisible factors
- Cannot be fully addressed — can't measure what you can't see
- Mitigation: baseline guardrails, randomized trial ordering, repeated trials
- Accept: in most cases the parameter signal is stronger than the shadow noise

## 7. Observer Effect

The measurement itself changes the system.

- Reconnaissance HTTP GET adds load, shifts cache state, triggers side effects
- Generally minimal for lightweight HTTP probes
- Mitigation: keep reconnaissance lightweight, compare with/without measurement

## 8. Phase Locking

Two breeders with similar trial cadence unintentionally synchronize.

- Breeder-1 always perturbs right when breeder-2 measures
- Creates systematic bias that looks like correlation but is just bad timing
- Unlikely in practice — would need very similar cadences
- Mitigation: jitter in trial intervals

## 9. Target Adaptation

The target learns or adapts to the optimization pattern.

- First 50 trials show clear relationships, then target compensates
- Relevant for targets with own feedback loops or adaptive behavior
- Niche case for most infrastructure targets

## General Mitigations (Cross-Cutting)

- **Canary guardrails**: always include metrics you're NOT optimizing as health checks
- **Baseline drift detection**: track unoptimized metrics to catch hidden changes
- **Measurement health**: track reconnaissance latency itself
- **Trial consistency**: repeat same parameters occasionally, compare results
- **Environment context logging**: record time, load, external state alongside trials

## Priority

1. Interference detection — novel, unsolved, high value
2. Delay awareness — partially solved, refine stabilization
3. The rest — monitor in production, address if observed
