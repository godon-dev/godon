# Bench Scenarios for Coupling Detection Experiments

Four scenarios that isolate individual mechanisms in multi-optimizer,
multi-target optimization. Each step adds exactly one variable.

## Overview

| Scenario | Breeders | Targets | Coupling | Purpose |
|----------|----------|---------|----------|---------|
| 1 | 1 | 1 | none | Baseline — single optimizer, single target |
| 2 | 1 | 2 | none | Multi-target — same params applied to both targets |
| 3 | 2 | 2 | none | Negative control — independent optimizers, no physical coupling |
| 4 | 2 | 2 | **yes** | **Experimental** — independent optimizers, hidden physical coupling |

## Experimental Design

Scenarios 1-4 form a progressive series:

- **1 -> 2**: Adds multi-target (does a single optimizer generalize?)
- **2 -> 3**: Adds multi-breeder (do independent optimizers produce spurious correlation?)
- **3 -> 4**: Adds hidden coupling (can coupling be detected above baseline correlation?)

The critical comparison is **scenario 3 vs 4** — identical breeder configs,
identical objectives, identical search space. The only difference is whether
the targets physically interact via the coupling channels. A coupling
detector should find signal in 4 but not in 3.

## Coupling Mechanism (Scenario 4 Only)

The greenhouse bench image supports inter-greenhouse coupling via environment
variables:

- `COUPLING_NEIGHBORS`: Comma-separated URLs of neighbor greenhouses
- `COUPLING_FACTOR`: Coupling strength (0.0 = none, 0.05 = weak, 0.2 = strong)

When coupling is enabled, each greenhouse fetches its neighbor's `/status`
endpoint on every `/apply` call and adjusts 4 hidden environmental variables:

| Channel | Neighbor metric | Affected variable | Effect |
|---------|----------------|-------------------|--------|
| Waste heat | avg temp | outside_temp | Neighbor heating warms local environment |
| CO2 exhaust | energy usage | outside_co2 | Neighbor energy use raises local CO2 |
| Power sag | energy usage | effective light | Neighbor draws power, dims local lights |
| Humidity drift | avg humidity | outside_humidity | Neighbor humidity shifts local humidity |

Neither breeder is aware of these channels. The coupling is invisible to
the optimization process — it only manifests as non-stationarity and
unexplained variance in trial outcomes.

## Directory Structure

Each scenario contains:
- `docker-compose.yml` — Target deployment (greenhouse bench containers)
- `breeders/` — Breeder configuration YAML files (submit to godon-api)

## Running

```bash
# Start targets
cd examples/bench/scenario-X
docker compose up -d

# Verify targets are healthy
curl http://localhost:8090/health
curl http://localhost:8091/health  # scenarios 2-4 only

# Submit breeder config(s) via godon-api
# (mechanism depends on deployment: Windmill, CLI, or API)
```

## Post-Hoc Analysis

After running scenarios 3 and 4, export trial histories from both breeders
and apply causal detection methods:

- **Granger causality**: Does past of breeder-1's outcomes predict
  breeder-2's outcomes beyond breeder-2's own history?
- **Cross-correlation of residuals**: After removing each optimizer's
  autoregressive component, do residual time series correlate?
- **Transfer entropy**: Non-linear information flow between optimizer traces.

Scenario 3 provides the false positive baseline. Scenario 4 provides the
true positive signal. Detection quality = true positive rate minus false
positive rate.
