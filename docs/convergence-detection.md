# Convergence Detection in godon-breeders Engine

## Status: Shelved

## Problem

The engine's `completion_criteria.quality_achieved` is currently a static flag — it never triggers. The breeder only stops on `iterations.min/max` or `timing.end`. There is no automated detection of whether the optimization has actually converged.

## Proposal

Add convergence detection to `godon-breeders/engine/breeder_worker.py` in the `_should_continue()` method. When the marginal improvement over a sliding window of trials drops below a configurable threshold, the engine sets `quality_achieved: true` and stops.

## Config Schema

```yaml
run:
  completion_criteria:
    iterations:
      min: 10
      max: 500
    timing:
      end: "1h"
    quality_achieved: true          # enable convergence check
    convergence:
      window: 10                     # sliding window of recent trials
      min_improvement: 0.01          # stop if improvement < 1% over window
      metric: "best_value"           # which metric to track
```

## Implementation

### Location

`godon-breeders/engine/breeder_worker.py` — `_should_continue()` method (currently around line 589).

### Logic

1. Maintain a deque of the last `window` best values from `self.study.best_trials`
2. After each trial, compute improvement rate: `(latest - oldest) / abs(oldest)`
3. If improvement rate < `min_improvement` AND trial count >= `min` iterations → set `converged = True`
4. `_should_continue()` returns `False` when converged
5. Final state update includes `convergence_reached: true` with the improvement value

### Pseudocode

```python
def _check_convergence(self):
    config = self.config.get('run', {}).get('completion_criteria', {})
    conv_config = config.get('convergence', {})

    if not config.get('quality_achieved', False):
        return False
    if not conv_config:
        return False

    window = conv_config.get('window', 10)
    min_improvement = conv_config.get('min_improvement', 0.01)

    trials = self.study.trials
    completed = [t for t in trials if t.state == TrialState.COMPLETE]

    if len(completed) < window:
        return False

    # Get best values from last `window` completed trials
    recent_values = []
    for t in completed[-window:]:
        if t.values:
            recent_values.append(t.values[0])  # primary objective

    if len(recent_values) < window:
        return False

    oldest = recent_values[0]
    latest = recent_values[-1]

    if abs(oldest) < 1e-10:
        return False

    improvement = abs(latest - oldest) / abs(oldest)

    logger.info(f"Convergence check: improvement={improvement:.4f} over {window} trials (threshold={min_improvement})")

    if improvement < min_improvement:
        logger.info(f"Convergence detected: {improvement:.4f} < {min_improvement}")
        self.metrics.set_converged(True)
        return True

    return False
```

### Integration into `_should_continue()`

```python
def _should_continue(self):
    # ... existing checks for iterations, timing ...

    if self._check_convergence():
        logger.info("Breeder stopping: convergence achieved")
        return False

    return True
```

### Metrics

- New gauge: `godon_breeder_convergence_improvement` — current improvement rate
- New gauge: `godon_breeder_converged` — 0 or 1
- State update: `wmill.set_state({'converged': True, 'improvement': improvement, ...})`

### E2E Integration

The E2E workflow can then check for convergence in addition to trial count:

```bash
CONVERGED=$(kubectl exec ... | grep 'godon_breeder_converged' | grep -oP '\} \K[0-9]+' | head -1)
if [ "${CONVERGED}" = "1" ]; then
  echo "Breeder converged"
fi
```

## Benefits

- Every strain automatically benefits from smart stopping
- Reduces wasted compute on converged optimizations
- E2E tests can validate actual optimization quality, not just "it ran"
- Configurable per-breeder — aggressive convergence for CI, relaxed for production

## Open Questions

- Should convergence check use best-value history or raw trial values? Best-value is smoother but hides exploration.
- Multi-objective: which objective to track for convergence? Configurable via `metric` field, default to primary.
- Should we also detect divergence (best value getting worse) and stop early?
