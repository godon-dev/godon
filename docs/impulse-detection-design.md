# Impulse-Based Interference Detection

## Core Insight

Impulse probing — sending deliberate extreme-value perturbations through
shared infrastructure and listening for echoes — is a universal method for
detecting interference across all channel types: linear, nonlinear,
cascaded, and non-stationary.

This collapses the channel-specific detection taxonomy (FFT for linear,
research for nonlinear, unknown for non-stationary) into a single approach
with a strength dial.

## Why It Works

Continuous signals (sines, codes) rely on frequency content surviving the
channel. Nonlinear transforms distort frequencies. Dead zones kill small
perturbations. Non-stationary channels shift characteristics mid-signal.

Impulses don't rely on frequency content. They rely on timing and
amplitude. You know WHEN the impulse was sent. You look for a response
in the receiver's objectives AFTER that timestamp. The encoding is
temporal, not spectral.

Non-stationarity is not a problem — impulses that land during sensitive
phases produce echoes. Ones that don't, don't. You just need enough
attempts that some land during sensitive windows.

Dead zones are not a problem — an impulse pushes parameters to extremes,
kicking the system OUT of dead zones into regions where the response
function has steep slopes.

Nonlinear transforms are not a problem — you're not trying to reconstruct
the signal. You're detecting whether ANY response occurred. Presence vs
absence, not frequency fidelity.

## Detection Method

Split receiver's objective values into:
- Post-impulse window: trials within N steps after sender's impulse
- Baseline: all other trials

Statistical test: rank-sum (Mann-Whitney U) or Kolmogorov-Smirnov.
Is the post-impulse distribution significantly different from baseline?

This is non-parametric. No assumptions about the distribution shape,
noise characteristics, or coupling channel properties.

## Practical Implementation

```
Normal trial:   params sampled by Optuna freely (pure optimization)
Impulse trial:  watermarked params pushed to extremes
                (e.g., all params at max or min of safe range)
```

Configuration:

```yaml
interference_detection:
  mode: active
  style: impulse          # "sine" for known-linear channels
  impulse_amplitude: extreme   # push to absolute bounds
  impulse_frequency: 0.02      # 1 in 50 trials (2% duty cycle)
  destructive: true            # operator accepts temporary disruption
  post_impulse_window: 5       # look for echo within N trials
```

The impulse frequency is inherently sparse — a 2% duty cycle means 98%
of trials are pure optimization. The destructive trials are flagged in
user_attrs (watermark: on) so the observer excludes them from
optimization quality metrics.

## Channel Strategy

```
Known linear?    -> sine watermark (cheap, non-destructive, FFT detection)
Unknown channel? -> impulse probe (universal, destructive, distribution test)
Confirmed safe?  -> downgrade to sine
```

Sine watermark is an optimization for the easy case. Impulse is the
universal fallback that works when you don't know the channel type.

## Why This Matters for the Greenhouse

The greenhouse bench has SNR ~0.002 with continuous sine watermarks —
the signal dies through 6+ nonlinear stages. FFT finds nothing at 200-300
trials.

An impulse at max amplitude sends a signal that is potentially 4-10x
stronger than the current 25% midpoint sine. The signal may still be
heavily distorted, but detection only needs presence, not fidelity. If
even one nonlinear stage passes a detectable perturbation, the impulse
echo will be visible as an outlier in the receiver's objectives.

This has NOT been tested. The greenhouse bench was never run with the
current clean watermark system, let alone impulse probing. The SNR
estimate of 0.002 is based on the old noisy watermark stacked on Optuna.
It may be completely wrong for impulse probing.

## Relation to Existing Methods

This is not a new invention. It's the standard approach in fields that
deal with hostile channels:

- **Seismology**: earthquake impulses through heterogeneous rock
- **Active sonar**: acoustic pings through nonlinear ocean layers
- **Ground-penetrating radar**: electromagnetic impulses through soil
- **Medical percussion**: tapping to detect fluid in tissue
- **Network traceroute**: ICMP packets through congested routers
- **Materials ultrasound**: acoustic pulses to detect cracks in metal

In every case, continuous signals fail because the channel is hostile.
Impulses succeed because they don't rely on the channel preserving
frequency content — only on it propagating a perturbation.

## Implications for Architecture

Impulses are inherently disruptive. They don't mix with optimization.
This forces the design decision that the current code was ducking:

Detection and optimization are different jobs. The options are:

1. **Dedicated probe agent**: exists only to send impulses, no
   optimization. Optimization breeders run untouched.
2. **Dedicated phase**: existing breeder switches to impulse mode for
   N trials, then back to optimization. Operator-visible pause.

The current approach (watermark on every trial, midpoint override)
is neither — it pretends to do both and does neither well.

## What's Proven

- Sine watermark + FFT + Rayleigh: works on linear channels (microgrid,
  coupling 0.0-0.9, 2 and 6 breeders)
- Impulse probing: NOT tested in godon. Theoretical basis is strong.
  Needs experiment.

## What to Test

1. Run greenhouse bench with impulse probing, distribution-shift detection
2. Compare with greenhouse bench under current sine watermark (also untested)
3. Find the impulse amplitude threshold: how extreme do params need to be?
4. Measure optimization impact of 2% impulse duty cycle
5. Test on microgrid at weak coupling (0.1) — does impulse detect what
   sine misses?

## Related

- `watermark-phase-design.md` — duty cycle and phase design discussion
- `watermarking-and-causal-discovery.md` — sine watermark theory
- `active-coupling-detection.md` — ABA choreography (pre-watermarking)
- `godon-documentation/material/docs/detection_capabilities.md` — channel taxonomy
