# Impulse Parameter Selection

## Current State

The impulse watermark pushes the **top 3 params by range size** to their bounds on every impulse trial. This is hardcoded in `create_watermark()`.

## Why Not All Params?

Sonar and seismology don't blast all channels simultaneously:

- **Seismology (Vibroseis)**: sweeps a single known frequency pattern across a band (20-150 Hz), then cross-correlates the return. One structured signal at a time.
- **Sonar (chirp/pulse compression)**: transmits a known sweep, correlates the echo. Not all frequencies at once — a structured pattern the receiver can match.
- **Matched filter principle**: the receiver knows exactly what was sent and looks for that specific pattern in noise.

For godon, pushing all params to extremes simultaneously creates **unstructured disturbance** — harder to correlate, more likely to trigger guardrails (observed: 12/51 trials failed with aggressive impulses). Every failed impulse is wasted — no data collected.

Coupling in the greenhouse scenario is environmental (shared temperature/humidity). Any param in the coupling path creates an echo in the receiver's objectives. The observer doesn't care WHICH param caused the echo — it stacks post-impulse objective windows.

## Open Design Questions

### Selection Strategy

Current: `top_n` by range size. Alternatives worth considering:

| Strategy | Description | Tradeoff |
|---|---|---|
| `top_n` | Largest range params (current) | Simple, covers params with most room to perturb |
| `all` | Every param with a range | Maximum disturbance, more guardrail failures |
| `random` | Random subset each impulse cycle | Diversity but non-deterministic |
| `sequential` | Cycle through params across impulses | Like Vibroseis sweep — structured coverage |
| `explicit` | User specifies which params | Full control, requires domain knowledge |

### Configurable Fields

```yaml
interference_detection:
  mode: active
  impulse:
    duty_cycle: 0.05
    direction: random
    # param_selection:
    #   strategy: top_n      # top_n | all | random | sequential | explicit
    #   max_params: 3         # for top_n/random strategies
    #   params:               # for explicit strategy
    #     - heating_setpoints
    #     - co2_injection
```

### Decision Points

1. **Default strategy**: `top_n` with `max_params: 3` is a reasonable default. Change when evidence warrants it.
2. **Should it be configurable now?** No — ship with top-3, gather bench data, then decide based on evidence.
3. **Sequential cycling**: Most interesting alternative. Instead of always perturbing the same 3 params, cycle through all params across impulse trials. Like Vibroseis sweeping across the band. Would give coverage of all coupling paths over time.
4. **Per-scenario tuning**: Greenhouse coupling is environmental (any param works). Other scenarios may have param-specific coupling paths where selection matters more.

## Evidence So Far

- Greenhouse bench with top-3: impulse spikes visible in live data, ~25% trial failure rate (12/51)
- Failure rate suggests top-3 may already be too aggressive for some parameter combinations
- Observer detection: not yet validated end-to-end (bench still running)
