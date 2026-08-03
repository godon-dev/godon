# Coupling Detection: Statistical Methods

Post-mortem of the statistical approach to coupling detection implemented in
godon-observer 0.5.0–0.8.0 and why we moved away from it.

## What We Built

Three statistical methods running client-side in the observer dashboard:

### Pattern Match (Cross-Correlation)

Computes Pearson correlation between first-differenced quality series of two
breeders at multiple lags. The highest correlation across lags is the score.

- **Intuition**: "Do these breeders move together?"
- **Preprocessing**: First-differencing (quality[t] - quality[t-1]) to remove
  shared growth trends
- **Threshold**: 0.3 (lowered from initial 0.4)

### Predictive Link (Granger Causality)

Tests whether breeder A's quality history improves prediction of breeder B's
quality beyond what B's own history provides. Uses OLS regression with
Gauss-Seidel iteration.

- **Intuition**: "Does knowing A help predict B?"
- **Implementation**: Compares restricted model (B predicts B) vs unrestricted
  model (A+B predict B) via F-test-like statistic
- **Threshold**: 0.1 (lowered from initial 0.3 — OLS produces realistic but
  small coefficients)

### Info Flow (Transfer Entropy)

Measures directed information flow from one series to another, based on
conditional probabilities of state transitions. Uses histogram binning with
inner-range outlier exclusion.

- **Intuition**: "Does information flow from A to B?"
- **Baseline**: Permutation test with 20 shuffles — compares observed TE
  against distribution of shuffled TEs, reports p-value as score
- **Bins**: 3 (reduced from 8 for sparse data)
- **Threshold**: 0.5 (p-value — raised from lower thresholds)

## What Worked

### First Differencing Was Essential

Raw composite quality is dominated by growth_rate (0–1 range swings). Linear
detrending was insufficient. First-differencing boosted signal:

- Raw correlation between coupled breeders: 0.038
- First-differenced correlation: 0.242 (6x improvement)

First-differencing works on heterogeneous breeders (different objectives) because
it analyzes *changes*, not absolute levels.

### Detection of Known Coupling (Scenario 4)

With COUPLING_FACTOR=0.5 (bidirectional coupling, greenhouse target):

- Pattern match: ~82.6% (correctly high)
- Info flow: ~60% in strongest direction (correctly directional)
- Asymmetry detected: one direction stronger than the other

### DAG Construction and Visualization

The shared `buildDag()` helper deduplicates pairs, strips cycles by removing
weakest edges, and produces clean directed acyclic graphs. The sankey, tree,
and topological visualizations all worked well.

## What Didn't Work

### The Fundamental Problem: Confounding

Both breeders independently converging on better solutions produces quality
trajectories that look correlated. This is indistinguishable from coupling
using observational data alone.

**Scenario 3 (no coupling, control)**:
- Pattern match: 33.8% (above 0.3 threshold — false positive)
- Info flow: 70% (far above 0.5 threshold — strong false positive)

Shared optimization dynamics (both breeders independently improving) produce
correlated first-differences. No statistical transformation can separate
"improving together because coupled" from "improving together because both
converging."

### Transfer Entropy Shuffle Baseline is Methodologically Flawed

Random permutation destroys autocorrelation structure in the time series. Any
series with smooth trends (i.e., every optimization trajectory) will look
"significantly different" from its shuffled versions.

This means TE will almost always report high significance for structured data,
regardless of whether coupling exists. Scenario 3's 70% score is an artifact of
the method, not evidence of coupling.

**Discussed alternative — circular shift permutations**: preserves
autocorrelation, only breaks timing relationships. Could reduce false positives
but introduces shift-length sensitivity and circular wrapping artifacts. Not
pursued.

### Pattern Match Self-Corrects Slowly (If At All)

Between 30 and 44 trials, scenario 3's pattern match dropped from 53.9% to
33.8%. This suggests it *might* eventually fall below the 0.3 threshold, but:

- Self-correction requires many trials (expensive)
- The rate of correction is unpredictable
- It may stabilize above the threshold permanently

### Threshold Tuning is a Losing Game

We iterated through multiple threshold values:

| Method        | Initial | Final | Problem                          |
|---------------|---------|-------|----------------------------------|
| Pattern match | 0.4     | 0.3   | Still fires on scenario 3        |
| Granger       | 0.3     | 0.1   | OLS values small, threshold arbitrary |
| TE            | varies  | 0.5   | Baseline is flawed anyway        |

Every threshold is either too sensitive (false positives) or too conservative
(misses real coupling). There is no principled way to set these values that
works across heterogeneous breeder configurations.

### The Specificity Problem in Summary

| Scenario | Coupling? | Pattern Match | Info Flow | Verdict     |
|----------|-----------|---------------|-----------|-------------|
| 3        | No        | 33.8% ⚠       | 70% ✗     | False positive |
| 4        | Yes (0.5) | 82.6% ✓       | 60% ✓     | Correct     |

Sensitivity is acceptable. Specificity is not. A detector that fires on nearly
every pair is useless as a trigger for automated response.

## Why We Moved Away From Statistical Detection

1. **No amount of threshold tuning fixes confounding** — shared optimization
   dynamics are structurally indistinguishable from coupling in quality data

2. **TE's permutation baseline is broken by design** — random shuffles destroy
   autocorrelation, making every structured series appear significant

3. **Layering statistical methods doesn't help** — all three methods see the
   same confounded signal; agreement between them doesn't increase confidence

4. **Statistical screening would trigger on nearly every pair** — making it
   an expensive no-op gate before real experiments

## What We Learned

- Observational inference (quality ↔ quality correlation) cannot distinguish
  "shared optimization dynamics" from "real coupling" with ~30–50 trials of
  noisy composite quality data
- Preprocessing matters enormously (first-differencing gave 6x signal boost)
  but cannot solve a fundamental confounding problem
- Transfer entropy requires careful baseline design — random permutation is
  inappropriate for time series with strong autocorrelation
- The only reliable signal requires some form of **counterfactual** — observing
  what happens when a breeder is absent vs present
- Statistical methods might still be useful as visualization (showing breeders
  move together) but not as automated detection

## See Also

- `stasis-patterns.md` — forms of stasis in optimization systems
- `context-aware-samplers.md` — context-aware sampler design for coupling-aware optimization
- godon-observer dashboard (`dashboard.html`) — cross-examination tab with all three methods
