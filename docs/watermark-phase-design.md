# Watermark Phase Design

Open design question: how should watermark probes interleave with
optimization trials?

## Current State

Watermark overrides Optuna's parameter suggestion on every trial for the
top 3 params by range (MultiFrequencyMultiParam). The base value is the
midpoint of the parameter range, not the sampler's choice. Optuna only
controls the remaining non-watermarked params.

Consequence: optimization is largely sidelined. The detection signal is
clean (proven at 6-breeder scale, coupling 0.9), but the breeder is not
meaningfully optimizing.

## The Design Question

Should watermark probes be:

### A. Dedicated Detection Phase

Pull over, inspect the car. Pause optimization. Run N watermark-only
probes. Analyze. Resume optimization.

Pros:
- Clean signal, proven to work
- Explicit and operator-visible ("running interference check")
- Easy to reason about and communicate

Cons:
- Requires a scheduler / choreographer to decide when to pause
- System state changes during pause — topology may be stale
- Optimization downtime
- Extra component to build and maintain

### B. Automatic Duty Cycle

Continuous monitoring. A configurable fraction of trials are watermark
probes (e.g. 2 of every 20). The rest are pure Optuna. No pause.

Pros:
- Self-contained, no scheduler needed
- Continuous rolling picture of interference state
- Configurable by changing one number (duty_cycle: 0.1)
- Matches how real systems monitor (pilot tones, heartbeats, health checks)

Cons:
- Weaker signal than dedicated phase — fewer samples at watermark frequency
- May not detect weak coupling at low duty cycles
- Needs more total trials to accumulate detection confidence

### C. Hybrid (Both)

Duty cycle for continuous monitoring. When duty-cycle detection flags a
potential interference, trigger a dedicated phase for precise analysis on
the flagged pairs only.

Analogy from the medical diagnostics doc: blood panel first (continuous),
MRI only where flagged (dedicated).

Pros:
- Best of both worlds
- Dedicated phase only runs when needed, minimizing optimization impact

Cons:
- Most complex to implement
- Needs a decision engine: when does continuous monitoring trigger a
  dedicated phase?

## Open Questions

- What duty cycle ratio works at coupling 0.5? 0.1?
- How many watermark samples does FFT+Rayleigh need for reliable detection
  at 10% duty cycle?
- Should the duty cycle be adaptive? Start high (aggressive detection),
  then reduce once topology is known?
- Who decides when to trigger a dedicated phase? The observer? The
  controller? A new component?
- Is the hybrid approach premature optimization of the design?

## What's Proven

- 100% duty cycle (every trial watermarked) works at coupling 0.9
- FFT + Rayleigh detection with permutation test works
- 6 breeders, 20 pairwise tests, high specificity
- Zero false positives

## What's Not Proven

- Any duty cycle below 100%
- Detection alongside real optimization (non-watermarked params changing)
- Whether the current SNR (~12.6 at 0.9 coupling) has enough margin to
  survive a 10x reduction in signal samples
- Detection at coupling factors below 0.5

## Related

- `watermarking-and-causal-discovery.md` — watermarking theory and validation
- `active-coupling-detection.md` — ABA choreography design (pre-watermarking)
- `context-aware-samplers.md` — sampler design for coupled environments
