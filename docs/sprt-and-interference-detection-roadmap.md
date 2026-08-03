# SPRT and Interference Detection Roadmap

Why we're replacing the fixed-sample MAD test with Sequential Probability Ratio
Testing (SPRT), and the phased plan for turning binary coupling detection into
learned interference relationships.

## The Problem with MAD

Current `computeShift` in the dashboard uses median absolute deviation (MAD) as
a fixed-sample test:

```
1. Collect exactly N observe-only trials during a pause
2. Compare "during pause" quality vs "outside pause" quality
3. If median shift > 0.5 * MAD → declare coupling
4. Always produces a yes/no answer regardless of confidence
```

This causes false positives (scenario 3 — independent targets flagged as
coupled) because:

- Small sample sizes (~5 trials) with high variance
- MAD is tiny when observe-only quality clusters (flat line), inflating shift
  ratio
- Zero-quality trials (failures) corrupt medians
- No consistency requirement — single noisy measurement declares coupling
- No notion of "I'm not sure yet" — always forced to answer yes or no

## SPRT: Sequential Probability Ratio Test (Wald, 1945)

### Core Idea

After every single trial, update a running score: "how much does the evidence
so far favor coupling vs no coupling?" Three outcomes:

- **Upper boundary crossed** → coupling detected, advance phase
- **Lower boundary crossed** → no coupling, advance phase
- **Between boundaries** → need more data, keep probing

### Why SPRT

- Proven optimal (Wald & Wolfowitz, 1948) — minimum expected sample size for
  given error rates
- No fixed sample size — stops early when effect is obvious, keeps going when
  ambiguous
- Error rates (α, β) are controlled by construction
- Matches our data arrival pattern: one trial at a time, sequential decisions

### MAD vs SPRT in Simple Terms

**MAD** = judge says "you get exactly 5 witnesses, then you must deliver a
verdict." After 5, forced to say guilty or innocent regardless of confidence.

**SPRT** = jury hears one witness at a time. After each: "sure enough to
convict?" / "sure enough to acquit?" / "call the next witness." If evidence is
overwhelming, stops early. If ambiguous, keeps going.

### Parameters

SPRT has two parameter types:

**Error rates α and β — policy choices, not data parameters:**

- α = false positive rate ("how often am I willing to cry wolf")
- β = false negative rate ("how often am I willing to miss real coupling")

Recommended hard-coded defaults:

```
α = 0.05 per pair per phase
β = 0.10 per pair per phase
```

Not configurable per breeder. These are a policy decision about organizational
risk tolerance, like a speed limit. Autoderive everything else, but error rates
are set once.

**Effect size threshold — autoderived from data:**

- μ₀ = baseline median from active trials before the pause (H0: no shift)
- δ = observed baseline MAD (minimum detectable shift)

```
H0: quality during pause has median μ₀       (no coupling)
H1: quality during pause has median μ₀ + δ    (coupling)

where δ = observed baseline MAD (derived from data)
```

MAD isn't thrown away — it becomes the ruler that defines what coupling means,
not the test that declares it. The test is SPRT. The ruler is MAD.

### Multiple Testing Correction

With N breeders there are N(N-1)/2 pairwise tests. Options:

1. **Replication requirement (recommended for Phase 1):**
   - α = 0.05 per pair, per phase, no correction
   - Require both observe phases to agree before declaring coupling
   - Two independent false positives at 0.05: 0.05 × 0.05 = 0.25%
   - Already stricter than Bonferroni at 5 breeders, no penalty on speed
   - The ABA choreography already has built-in replication

2. **Benjamini-Hochberg FDR (if needed at scale):**
   - Instead of "≤5% chance of ANY false coupling" (Bonferroni), use "≤5% of
     declared couplings are false" (FDR)
   - Scales well — at 10 breeders, α per pair ≈ 0.044 (essentially no penalty)
   - Apply after all pairs in a phase reach verdict

3. **Bonferroni (too conservative, not recommended):**
   - α_per_pair = 0.05 / num_pairs
   - At 10 breeders: α = 0.001 per pair — overly demanding

### Implementation

```
class SPRT:
    def __init__(self, mu0, delta, alpha=0.05, beta=0.10):
        self.mu0 = mu0              # baseline median (derived)
        self.sigma = delta          # min detectable shift = baseline MAD (derived)
        self.upper = math.log((1 - beta) / alpha)
        self.lower = -math.log((1 - alpha) / beta)
        self.log_likelihood = 0.0

    def update(self, observation):
        # Normal likelihood ratio, one observation
        z = (observation - self.mu0 - self.sigma / 2) / self.sigma
        self.log_likelihood += self.sigma * z / self.sigma  # simplified
        # Full form: log(f1(x)/f0(x)) where f0=N(mu0,sigma), f1=N(mu0+delta,sigma)

        if self.log_likelihood >= self.upper:
            return "coupling"      # H1 accepted
        elif self.log_likelihood <= self.lower:
            return "no_coupling"   # H0 accepted
        else:
            return "continue"      # need more data
```

Where to implement:

- **Breeder engine**: `godon-breeders/engine/breeder_worker.py` — phase
  completion logic in the choreography state machine
- **Dashboard**: `godon-images/images/godon-observer/src/dashboard.html` —
  `computeShift()` function and cross-examination analysis

### Nonparametric Fallback

If quality distributions turn out to be very non-normal (heavy tails, bimodal),
swap the likelihood function from Normal to a rank-based (Wilcoxon) or bootstrap
likelihood. The SPRT framework stays the same — just swap what feeds into the
log-likelihood accumulator.

For the dashboard's post-hoc analysis (where all data is available), use a
permutation test or Wilcoxon signed-rank on the completed data for clean
p-values without distributional assumptions.

## Speed Optimizations

SPRT is the first speed improvement (variable sample size), but not the only
one. The full set of near-term improvements:

### 1. SPRT Stops Early (Phase 1, implement now)

Instead of fixed 5-trial phases, SPRT decides after each trial. Obvious
coupling detected in 2 trials. No coupling declared in 3-4. Estimated ~40%
reduction in average phase time.

### 2. Pause One, Measure All (Phase 1, implement now)

Currently: pause A, check B only. Better: pause A, check B, C, D, E
simultaneously. All other breeders can observe during the same pause window.
Turns N² sequential rounds into N rounds.

### 3. Skip Impossible Pairs (Phase 1, implement now)

Use infrastructure metadata to prune the test matrix before testing. Breeders
on completely separate infrastructure can't interfere. 10 breeders might have 45
pairs, but only 12 share any infrastructure.

### 4. Staggered Choreography (Phase 2)

Overlap ABA rounds. While pair (A,B) is in observe phase, pair (A,C) can be in
active phase. Pipeline the choreography instead of serializing it.

### 5. Active Probing (Phase 2)

Don't passively observe while paused. Send targeted small perturbations
designed to maximize information gain (active learning). Fewer trials needed
because each trial is chosen to be maximally informative.

## Phased Roadmap

### Phase 1: Detect + Work Around (current)

- SPRT replaces fixed-sample MAD in breeder engine
- Binary output: coupled / not coupled
- Breeders take turns via choreography
- Speedups: early stopping, pause-one-measure-all, skip impossible pairs

### Phase 2: Learn the Coupling Function

- During observe-only phases, fit a lightweight model: "when A's parameter X is
  at value v, B's quality shifts by f(v)"
- Turns binary detection into a quantitative relationship
- Observe-only trials serve double duty: detection AND modeling

### Phase 3: Parameter-Space Dependency Map

- Instead of "A and B interfere," learn "A's learning rate above 0.01 causes
  B's accuracy to drop 15%"
- Share back to breeders as constraints: "don't exceed X on parameter Y"
- Breeders self-constrain and stop needing to pause for known interference

### Phase 4: Predict Unknown Couplings

- With A→B and A→C learned, reason about B↔C without testing
- Build an interference graph incrementally
- Skip testing transitively predictable pairs
- Addresses the N² scale problem

### Phase 5: Self-Managing

- Structured perturbations chosen for maximum information gain (active learning)
- New coupling → constraint added → no more pausing for that pair
- System converges to zero choreography overhead as it learns the interference
  landscape
- Essentially multi-task BO emerging bottom-up from independent agents sharing
  constraints

## Landscape: Where Godon Fits

| Method | Assumes | Limitation | Realistic? |
|---|---|---|---|
| Single-optimizer (Optuna, Vizier) | One target, no interference | Can't handle interactions | One thing at a time only |
| Multi-task BO | Central control, shared model, joint objective | Can't cross team boundaries | Lab conditions |
| A/B testing (Optimizely) | Discrete treatments, one metric | No continuous optimization | Marketing, not engineering |
| Observational causal (DoWhy, causaLens) | Historical data, no interventions | Can suggest but not prove | Analysis, not action |
| Multi-agent RL | Shared reward, joint training in simulation | No shared reward in production | Games and robotics |
| **Godon** | Multiple optimizers, shared environment, can pause | Slower convergence than centralized BO | **Production reality** |

Godon's only assumptions:

1. Multiple things are being optimized concurrently
2. They share an environment (infrastructure, data, users)
3. Participants can take turns (pause/resume)

No central model, no shared objective, no simulation, no manual experiment
design. The novelty is the concept — autonomous experimental causal discovery
between concurrent continuous optimizers — not any individual statistical
method.

The statistical pieces (SPRT, BH, alpha-spending, sequential design) are solved
problems from clinical trials (Wald 1945, Lan & DeMets 1994, Jennison &
Turnbull 1999) and genomics (Benjamini & Hochberg 1995). Nobody has combined
them into a system that detects interference between independent optimizers
running in a shared environment.

## References

- Wald, A. (1945). Sequential Tests of Statistical Hypotheses. *Annals of
  Mathematical Statistics*, 16(2), 117-186.
- Wald, A. & Wolfowitz, J. (1948). Optimum Character of the Sequential
  Probability Ratio Test. *Annals of Mathematical Statistics*, 19(3), 326-339.
- Lan, K.K.G. & DeMets, D.L. (1994). Interim Analysis: The Alpha Spending
  Function Approach. *Statistics in Medicine*, 13, 1341-1352.
- Jennison, C. & Turnbull, B.W. (1999). *Group Sequential Methods with
  Applications to Clinical Trials*. Chapman & Hall/CRC.
- Benjamini, Y. & Hochberg, Y. (1995). Controlling the False Discovery Rate.
  *Journal of the Royal Statistical Society*, Series B, 57(1), 289-300.

## Watermark Injection for Parameter-Level Coupling Discovery

Current ABA detects breeder-level coupling ("A and B are coupled"). Watermark
injection discovers parameter-level coupling ("A's somaxconn above 1024 causes
B's latency to increase 30%").

### Concept

Instead of holding still during observe-only phases, the paused breeder injects
a known parameter pattern (watermark):

```
A's parameter during pause: [baseline, +10%, baseline, -10%, baseline, +10%]
If B's quality mirrors:     [normal,  up,    normal,  down,  normal,  up   ]
→ A's parameter causally affects B, magnitude directly measurable
```

### Why Watermarks

- **Which parameter** — watermark each parameter independently with different
  patterns (e.g., sine waves at different frequencies)
- **Effect level** — B's response amplitude directly measures coupling strength
- **Noise immunity** — known patterns are distinguishable from random noise
  (spread-spectrum communication applied to causal discovery)
- **No false positives** — random noise won't reproduce a deliberate pattern
- **No additional trials needed** — watermarks replace passive observe-only with
  active probing within the same trial budget

### Implementation Sketch

Each parameter gets a watermark function during observe-only:

```python
def watermark(phase_idx, trial_idx, base_value, amplitude=0.1):
    freq = parameter_index + 1  # unique frequency per parameter
    return base_value * (1 + amplitude * math.sin(2 * math.pi * freq * trial_idx / period))
```

On the measuring side, detect which frequencies appear in B's quality signal
using FFT or autocorrelation. Each detected frequency maps to a specific
parameter in A.

### Relation to SPRT

SPRT still decides when enough evidence has accumulated. But instead of
accumulating raw quality differences, it accumulates correlation between the
known watermark pattern and the observed quality signal. This is much more
sensitive — you can detect coupling even when the effect is buried in noise.

## Replication Requirement Fix

The current dashboard requires `replicateCount >= 2` (two shared observe phases
between a pair) to declare "coupled." This is impossible in a single
choreography round where each pair is tested once.

Options:
1. Remove replication requirement — rely on p < 0.05 from permutation test
2. Check replication across multiple choreography records (requires persistence)

For now, the permutation test with p < 0.05 is sufficient. Replication across
rounds is a future enhancement.

## See Also

- `coupling-detection-statistical-methods.md` — post-mortem of the previous
  observational approach (cross-correlation, Granger, transfer entropy) and why
  it was abandoned
- `active-coupling-detection.md` — ABA choreography design
- `extensions-and-advancements.md` — broader strategic context
