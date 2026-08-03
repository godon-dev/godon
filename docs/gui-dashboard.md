# godon-observer: Optimization Observability Service

## Status: In Progress

## Problem

Optimization progress is currently invisible without SSH-ing into pods and running raw Prometheus queries or SQL. There is no way for the quorum (humans + AI minds) to intuitively observe trial progress, guardrail compliance, and convergence in real-time.

## Proposal

Extend `godon-metrics-exporter` into `godon-observer` — a single Rust service that provides Prometheus metrics (existing), per-trial data from Optuna storage (new), and an embedded visualization dashboard (new). No Python dependency. No separate GUI image.

## Image

`godon-observer` in `godon-images`. Supersedes `godon-metrics-exporter`. Same build pipeline, same Nix pattern, same tag workflow (`godon-observer-X.Y.Z`).

## Architecture

```
Prometheus (data source)
    ↓ HTTP API
godon-gui (nginx serving static HTML + JS)
    ↓ browser renders
heatmap | spider web | parallel coordinates
```

No backend logic. The GUI is a pure frontend that queries Prometheus directly from the browser.

## Image Structure

Follows existing godon-images pattern:

```
images/godon-gui/
  default.nix          # nginx-based OCI image
  src/
    index.html         # single-page app
    app.js             # dashboard logic
    style.css          # styling
```

Since there's no Rust code, the `default.nix` builds a simple nginx image serving static files — no Cargo.toml needed.

## Visualizations

### 1. Heatmap (default view)

- Rows = metrics (growth_rate, max_temp, max_co2, energy_kwh, water_liters)
- Columns = trials ordered chronologically
- Cell color = value on a gradient (red=bad, green=good)
- Guardrail thresholds shown as horizontal markers on each row
- Convergence visible as columns stabilizing in color rightward

### 2. Spider Web (detail view)

- One axis per metric radiating from center
- Current best trial shown as filled polygon
- Guardrail boundary shown as dashed red outline
- Shape evolution visible via trial slider
- Violations obvious when polygon extends past guardrail outline

### 3. Trial Slider

- Slider at bottom of visualization area
- Scrubs through trials 1→N
- Heatmap columns highlight, spider web updates, parallel coordinates filter
- Color-coded bar segments: green=improved/within guardrails, red=violation/regression

### 4. Parallel Coordinates (analyst view)

- Each metric gets a vertical axis with its own scale
- Each trial drawn as a line connecting values across axes
- Brushing: drag-select range on one axis to highlight matching trials
- Reveals which parameter combinations produce good outcomes
- Guardrail thresholds marked on each axis

### 5. Breeder Selector

- Dropdown listing active breeders from Prometheus labels
- Switches all visualizations to selected breeder
- Shows breeder metadata: type, trial count, best value, status

## Data Source

Prometheus HTTP API queries:

```
# All breeders
godon_breeder_total_trials
godon_breeder_best_value
godon_breeder_effectuation_total
godon_breeder_trial_duration_seconds

# Per-trial detail requires either:
# a) Pushgateway raw metrics (current approach)
# b) New trial-level metric exposition (future)
```

### Limitation

Prometheus stores aggregated gauges/counters, not individual trial results. For per-trial detail (each trial's exact metric values), we need one of:

- **Option A**: Query the Windmill Postgres completed jobs table (requires backend proxy)
- **Option B**: Exporter exposes trial-level time series with trial number as label
- **Option C**: Breeder writes trial artifacts to shared storage (future)

For v1, work with what Prometheus has (aggregated metrics). Per-trial detail is a v2 concern.

## Deployment

### In-cluster (primary)

```yaml
# charts/godon/values.yaml
gui:
  image:
    repository: "ghcr.io/godon-dev/godon-gui"
    tag: "0.0.1"
    pullPolicy: IfNotPresent
  replicas: 1
  port: 80
  service:
    type: ClusterIP
```

Exposed via the same ingress as the API. Served at `/dashboard/` or a separate subdomain.

### Local

```bash
docker run -p 8080:80 ghcr.io/godon-dev/godon-gui:0.0.1
# Dashboard at http://localhost:8080
# Prometheus URL configured via env var or query param
```

## Build & Release

Follows the standard godon-images pattern:

- CI workflow: `godon-gui-ci.yml` — builds on PRs touching `images/godon-gui/**`
- Release workflow: `godon-gui-release.yml` — triggers on tag `godon-gui-X.Y.Z`
- Shared release pipeline via `release-image.yml`
- Published to `ghcr.io/godon-dev/godon-gui`

## Config

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMETHEUS_URL` | `http://godon-observability-prometheus-server.godon-observability.svc:9090` | Prometheus endpoint |
| `REFRESH_INTERVAL` | `5s` | Auto-refresh rate |
| `DEFAULT_BREEDER` | (empty) | Pre-select breeder on load |

## Implementation Steps

1. Create `images/godon-gui/` in godon-images with `default.nix` and static HTML/JS
2. Adapt the existing prototype (`docs/viz-prototype.html`) to query real Prometheus data
3. Add CI/release workflows
4. Add Helm chart templates in godon-charts
5. Tag `godon-gui-0.0.1`, push, verify

## Prototype

A working prototype with mock data exists at `docs/viz-prototype.html` in the godon repo. It demonstrates heatmap, spider web, parallel coordinates, trial slider, and brushing.

## Open Questions

- How to get per-trial metric values? Prometheus only stores aggregated gauges. May need exporter changes or a lightweight backend proxy to Windmill's Postgres.
- Should the GUI image include a small backend for API calls (breeder list, trial detail), or stay pure static?
- Auth: use the same auth as the API, or keep the dashboard open within the cluster?
- Mobile responsive? The quorum might review on tablets/phones.
