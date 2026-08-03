# Impulse Detection: Fundamental Assessment

Honest evaluation of whether matched filter + CFAR + round-level stacking is
the right approach for the godon interference detection problem, given the
actual signal characteristics.

## Executive Summary

The **active probing paradigm is sound** — injecting known signals and measuring
the response is the correct approach (the observational post-mortem confirms
passive methods fail due to confounding). But the **stimulus design and detector
are mismatched to the actual signal**, and this is fixable without abandoning
the paradigm. The signal IS detectable with the right methods.

Three problems, in priority order:

1. **Stimulus mismatch**: single-trial impulses excite the thermal-mass channel
   at frequencies it cannot reproduce. The ping/listen oscillation is smeared to
   DC. Need sustained block excitation (AB design).

2. **Detector mismatch**: the matched filter looks for an oscillating echo
   (ping elevated, listen not). The coupling is a sustained step function. Need
   change-point detection (CUSUM) or a GLM with a modeled impulse response.

3. **Drift confounding**: round-level stacking compares two time periods, but
   the nonstationary baseline drifts on the same order as the coupling signal.
   Need difference-in-differences or explicit drift modeling.

---

## The Numbers: Is the Signal Detectable at All?

Before discussing algorithms, verify the signal is not fundamentally below the
detection limit.

```
Noise std (hold phase)    σ = 0.06    (on growth_rate, 0–1 scale)
Coupling shift            Δ = 0.04
Per-sample SNR            Δ/σ = 0.667
```

A single sample has less signal than noise — no single-trial classifier can
work. But coherent averaging of N independent samples:

```
SNR_mean = Δ / (σ/√N) = 0.667 × √N

  N=10  → SNR = 2.1   (below typical 2.5 threshold)
  N=15  → SNR = 2.6   (borderline)
  N=20  → SNR = 3.0   (detectable)
  N=35  → SNR = 4.0   (confident)
  N=50  → SNR = 4.7   (very confident)
```

**Verdict: the signal IS detectable** with ~20+ samples per condition, provided
the noise is approximately independent and the baseline is properly referenced.
The problem is not physics — it's methodology. We are leaving detectable signal
on the table.

Caveat: these numbers assume iid noise. If the hold-phase noise is
autocorrelated (greenhouse state persists across trials), the effective sample
size N_eff < N, and more samples are needed. The thermal time constant that
sustains the coupling signal also correlates the noise.

---

## Problem 1: Stimulus Mismatch (THE primary issue)

### What the code does

The sender alternates single-trial impulses:
```
Trial t:   ping   (extreme params, 1 trial)
Trial t+1: listen (baseline params, 1 trial)
Trial t+2: ping
Trial t+3: listen
...
```

This is a square wave at period 2 trials (frequency = 0.5 cycles/trial).

### Why it fails

The greenhouse has thermal mass. The coupling channel is a low-pass filter with
time constant τ. If τ >> 1 trial period (15 seconds), the filter output for a
square-wave input is:

```
DC component:     mean of extreme and baseline values (the average)
AC component:     attenuated by ~T/(πτ) → approaches zero as τ grows
```

The receiver sees a nearly **constant** elevated level — the average of ping
and listen responses — with almost no ping/listen contrast. The matched filter
computes `ping_mean - listen_mean ≈ 0`.

The code itself acknowledges this at line 594:
> "If most pairs are degenerate (aliased), the ping/listen frequency exceeds the
> receiver's sampling rate (Nyquist)."

This is not a sampling-rate problem — it's a **bandwidth** problem. The thermal
channel cannot reproduce a 2-trial-period oscillation regardless of sampling
rate. It's like trying to send a 1 kHz signal through a 10 Hz low-pass filter
and then blaming the ADC.

### The fMRI analogy

This is the exact problem fMRI faced and solved. In fMRI:
- Stimulus: brief neural events (analogous to our impulses)
- Channel: hemodynamic response — SLOW, sustained, peaks ~6s post-stimulus
- Solution: block design (sustained 20–30s stimulation blocks) instead of
  event-related (single-trial events), because the hemodynamic response function
  (HRF) is a low-pass filter that smears brief events

**The greenhouse thermal mass IS a hemodynamic response function.** The same
design principles apply.

### Fix: block design (AB or ABA)

Instead of alternating ping/listen every trial, use sustained blocks:

```
Block A (baseline):     10–20 trials at baseline params
Block B (intervention): 10–20 trials at extreme params
Block A' (recovery):    10–20 trials at baseline params (ABA for reversibility)
```

This gives the thermal mass time to reach steady state within each block,
maximizing the contrast between blocks. With 15+ samples per block and the math
above, the step is clearly detectable.

Tradeoff: block design is slower per detection decision (30–60 trials vs 20).
But the current impulse design produces zero usable contrast, so "slower but
works" beats "fast but blind."

---

## Problem 2: Detector Mismatch

### What the code does

Two detectors run in parallel:

**Matched filter** (lines 728–812): stacks receiver values during ping vs listen
phases, computes `matched_shift = ping_mean - listen_mean`, normalizes by noise
std. This is equivalent to correlating the receiver signal with a single-cycle
square wave — it assumes the receiver oscillates in phase with the sender.

**Round-level stacking** (lines 599–701): compares receiver values during the
impulse window vs before it. Computes `shift = stacked_mean - baseline_mean`,
normalizes by baseline std. This is a two-sample mean comparison.

### Why the matched filter is the wrong detector

A matched filter is the **optimal** linear detector when you know the exact
received signal shape (Kay, *Fundamentals of Statistical Signal Processing,
Vol. II: Detection Theory*, 1998). In radar/sonar, the received echo is a
delayed, attenuated copy of the transmitted pulse — the shape is known.

Here, the received signal is NOT a copy of the transmitted square wave. The
thermal channel transforms it into a **smoothed step/ramp**. The code correlates
against the transmitted shape (square wave), not the received shape (step). This
is a fundamental mismatch — you're using the wrong template.

The fix is NOT to use a different template with the same matched-filter
framework. The fix is to use a detector designed for step changes.

### The right detector: change-point detection

The coupling signal is a **sustained step function**. The canonical algorithm
for detecting a step change in noisy data is **change-point detection** (also
called structural break detection):

**CUSUM (Cumulative Sum)** — Page (1954):
```
S₊(t) = max(0, S₊(t-1) + (x(t) - μ₀ - k))
S₋(t) = min(0, S₋(t-1) + (x(t) - μ₀ + k))

Detect when |S₊| or |S₋| exceeds threshold h.
```
where μ₀ is the baseline mean and k = Δ/2 is the reference value (half the
expected shift).

CUSUM is provably optimal — it minimizes the worst-case average detection delay
for a given false-alarm rate (Lorden, 1971). It is designed exactly for this
scenario: a sustained mean shift in noisy data. It's the standard in quality
control, intrusion detection, and finance.

**Other options:**
- ** Shiryaev-Roberts** — similar to CUSUM, Bayesian-optimal for average delay
- **EWMA control chart** — exponentially weighted moving average, simple and
  robust to non-normality
- **Pruned Exact Linear Time (PELT)** — offline multiple change-point detection
  (Killick et al., 2012), if analyzing a completed run

### Alternative: GLM with modeled impulse response

If you keep the impulse stimulus (not recommended — see Problem 1), model the
greenhouse's impulse response explicitly:

1. Estimate the thermal time constant τ from data (exponential fit to step
   response)
2. Construct the predicted response: convolve the sender's impulse train with
   the estimated impulse response function (IRF)
3. Correlate the predicted response with the actual receiver signal

This is exactly the fMRI GLM approach. The predicted response captures the
smoothing/delay, so the correlation has real signal to work with.

This is strictly better than the current "correlate against the raw square wave"
approach, but strictly worse than switching to a block design + CUSUM (which
sidesteps the need to estimate τ accurately).

---

## Problem 3: Drift Confounding

### What the code does

Round-level stacking compares:
- `round_stacked`: receiver trials during the impulse window (first_imp - 30s
  to last_imp + 120s)
- `round_baseline`: receiver trials BEFORE the first impulse

### Why it's borderline

These are two **different time periods**. The greenhouse drifts over time
(nonstationary baseline). If the drift rate is d per trial and the two windows
are separated by K trials, the drift contributes K×d to the measured shift:

```
Measured shift = coupling_shift ± drift_contamination
               = 0.04 ± K × d
```

If K = 20 trials and d = 0.002/trial, drift adds ±0.04 — **equal to the coupling
signal itself**. The detector sees a shift somewhere between 0.0 and 0.08 and
can't tell which part is real.

This is the same confounding problem the observational post-mortem identified,
just in a different guise: comparing two time periods cannot separate "shift
due to coupling" from "shift due to time passing."

### Fix: difference-in-differences

If a simultaneous control is available (an uncoupled breeder or a reference
greenhouse running in parallel), use difference-in-differences:

```
True coupling effect = (receiver_during - receiver_before)
                     - (control_during  - control_before)
```

Both receiver and control experience the same drift, so it cancels. Only the
coupling-specific shift remains.

### Fix: local differencing / paired design

If no simultaneous control exists, pair each impulse trial with the immediately
preceding baseline trial:

```
diff(t) = receiver(t+lag) - receiver(t)
```

where t is the impulse onset and lag is the propagation delay. This is a
within-subject comparison that's robust to slow drift (the drift over 1–2
trials is negligible). Stack the diffs across impulse events.

This is essentially what the matched filter TRIES to do (ping vs listen), but
the block design makes the diff meaningful because the step has time to develop.

### Fix: explicit drift modeling

Fit the receiver signal as:
```
receiver(t) = baseline(t) + coupling × stimulus(t) + ε
where baseline(t) = a + b×t (linear drift, or low-order polynomial)
```

This is a regression with the stimulus as a regressor and drift as a covariate.
The coupling coefficient and its t-statistic give you the detection. This is
the fMRI GLM approach with drift regressors (high-pass filter or polynomial).

---

## Problem 4: Implementation Issues in the Current Code

Beyond the fundamental issues, the implementation has bugs/limitations:

### CFAR threshold is effectively disabled (line 794–795)

```rust
let adaptive_threshold = cfar_alpha / (matched_pairs as f64).sqrt();
let detected = matched_snr >= adaptive_threshold.max(snr_threshold);
```

With cfar_alpha = 3.0 and any matched_pairs ≥ 2:
`adaptive_threshold = 3/√2 = 2.12`, which is below snr_threshold (2.5).

The `.max(snr_threshold)` means the effective threshold is ALWAYS 2.5. The CFAR
adaptation never actually adapts — it's dead code. The detector is a fixed-
threshold SNR test, not CFAR.

### Noise estimate is contaminated (lines 777–788)

The noise_std uses listen-phase variance. But if coupling is sustained (thermal
mass), listen-phase values are ALSO elevated. While a constant shift doesn't
change variance, a ramping response (coupling building up over the impulse
round) does inflate the variance, suppressing SNR.

The fallback to `1e-6` (line 786) when fewer than 5 listen samples exist is
dangerous — it produces SNR in the billions (the code comment acknowledges this).

### Round window definitions are heuristic (lines 651–660)

```
round_stacked: first_imp - 30s to last_imp + 120s
round_baseline: < first_imp - 10s
```

The 30s pre-buffer and 120s post-buffer are arbitrary. The pre-buffer may include
pre-impulse receiver trials that aren't actually "during" coupling. The baseline
cutoff at first_imp - 10s excludes a 10s gap that has no physical justification.

### Alias detection is correct but the fallback is weak (line 594)

The code correctly detects when ping and listen alias to the same receiver trial
(degenerate pairs). But the fallback (round-level stacking) inherits the drift
problem described above.

---

## Recommendations: What to Actually Do

### Tier 1: Change the stimulus (highest impact, lowest algorithmic complexity)

Switch from single-trial ping/listen impulses to **sustained block excitation**:

```
Phase 1 (baseline):    receiver holds, sender at neutral params, 15+ trials
Phase 2 (intervention): receiver holds, sender at extreme params, 15+ trials
Phase 3 (recovery):    receiver holds, sender at neutral params, 15+ trials
```

This is the ABA / single-case experimental design (SCED) from behavioral
science. It's the gold standard for detecting sustained intervention effects in
noisy, drifting systems.

With 15+ trials per phase and per-sample SNR = 0.67:
- SNR of phase-mean contrast = 0.67 × √15 = 2.6 → detectable
- With 20 trials: 0.67 × √20 = 3.0 → clearly detectable

### Tier 2: Change the detector

Replace the matched filter + CFAR with **CUSUM** on the receiver signal:

```python
# Online (sequential) version — runs as trials arrive
def cusum_stream(x, mu0, delta, sigma, h=None):
    k = delta / 2                        # reference value
    h = h or 5 * sigma                    # threshold (~5σ false alarm rate)
    s_pos, s_neg = 0.0, 0.0
    for i, xi in enumerate(x):
        s_pos = max(0, s_pos + (xi - mu0 - k))
        s_neg = min(0, s_neg + (xi - mu0 + k))
        if s_pos > h:
            return ("up", i)              # upward step detected at trial i
        if s_neg < -h:
            return ("down", i)            # downward step detected at trial i
    return ("none", len(x))
```

For offline analysis (post-run), also consider:
- **PELT** (Killick et al., 2012) for detecting multiple change points
- **Bayesian online change-point detection** (Adams & MacKay, 2007) for
  uncertainty quantification

### Tier 3: Handle the drift

If a simultaneous control breeder exists:
- **Difference-in-differences**: subtract control trajectory from receiver
  trajectory before detection

If not:
- **Local differencing**: pair each intervention trial with the nearest baseline
  trial (within ±2 trials) and stack the differences. Drift over 2 trials is
  negligible.
- **Polynomial detrending**: fit and remove a low-order (degree 1–2) polynomial
  from the receiver trajectory before CUSUM.

### Tier 4: Keep impulse design only if you model the IRF

If switching to block design is infeasible (operational constraints), then at
minimum:
1. Estimate the greenhouse impulse response (exponential decay with time
   constant τ, fit from data)
2. Convolve the sender's stimulus train with the IRF to get the predicted
   receiver response
3. Correlate predicted response with actual receiver signal
4. Use a permutation test for significance (shuffle the stimulus-reservation
   pairing, recompute correlation, build null distribution)

This is the fMRI GLM approach. It's more complex than CUSUM on block data but
works with the existing impulse infrastructure.

---

## Analogous Real-World Problems and Their Solutions

| Domain | Signal type | Channel | Method used |
|--------|------------|---------|-------------|
| Active sonar/radar | Echo (delayed copy) | Reflection | Matched filter ✓ |
| fMRI | Neural events (brief) | Hemodynamic (low-pass) | GLM + HRF, block design |
| Seismology | Transient waves | Earth medium | STA/LTA, template matching, CUSUM |
| Quality control | Process mean shift | Manufacturing | CUSUM, EWMA charts |
| Finance | Regime change | Market dynamics | Change-point tests (Bai-Perron) |
| Clinical trials | Treatment effect | Patient biology | Sequential tests (SPRT), ITT |
| **Godon (current)** | Impulse | Thermal mass (low-pass) | **Matched filter ✗** |
| **Godon (proposed)** | Block step | Thermal mass (low-pass) | **CUSUM / GLM ✓** |

The pattern is clear: when the channel is a low-pass filter (thermal mass,
hemodynamics), you need either block design + change-point detection or GLM with
modeled impulse response. Matched filtering against the raw stimulus is wrong.

---

## Should We Abandon Active Probing Entirely?

**No.** The post-mortem (`coupling-detection-statistical-methods.md`) established
that observational methods (cross-correlation, Granger, transfer entropy) fail
due to confounding with shared optimization dynamics. The conclusion was:

> "The only reliable signal requires some form of counterfactual — observing
> what happens when a breeder is absent vs present."

Active probing (injecting known signals) IS the counterfactual. The problem is
not the paradigm — it's that:
1. The stimulus is too fast for the channel (impulse vs thermal mass)
2. The detector assumes the wrong signal shape (oscillation vs step)
3. The baseline comparison is confounded by drift

Fixing these three things transforms the approach from "blind" to "working."

---

## Specific Algorithm References

- **CUSUM**: Page, E.S. (1954). "Continuous Inspection Schemes." *Biometrika*,
  41(1/2), 100–115. Optimal for sustained mean shift detection.
- **PELT**: Killick, R., Fearnhead, P., & Eckley, I.A. (2012). "Optimal
  Detection of Changepoints with a Linear Computational Cost." *JASA*, 107(500),
  1590–1598.
- **fMRI GLM/HRF**: Friston, K.J. et al. (1994). "Statistical Parametric
  Mapping." *Human Brain Mapping*, 2(4), 189–210. The HRF convolution approach.
- **Shiryaev-Roberts**: Shiryaev, A.N. (1963). "On Optimum Methods in Quickest
  Detection Problems." *Theory Prob. Appl.*, 8(1), 22–46.
- **Bayesian change-point**: Adams, R.P. & MacKay, D.J.C. (2007). "Bayesian
  Online Changepoint Detection." arXiv:0710.3742.
- **SCED (single-case design)**: Horner, R.H. et al. (2005). "The Use of
  Single-Subject Research to Identify Evidence-Based Practice in Special
  Education." *Exceptional Children*, 71(2), 165–179.
- **Difference-in-differences**: Card, D. & Krueger, A. (1994). "Minimum Wages
  and Employment." *AER*, 84(4), 772–793. The canonical DiD reference.
