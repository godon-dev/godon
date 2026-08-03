# Session 2026-07-31 — Chain4 Composition Validated

## Achievement

Chain4 topology fully validated: 4 nodes, 3 edges (0.7, 0.5, 0.3), all detected
with measured coupling matching planted ground truth.

```
node-1 → node-2 (0.7): rising=0.345  expected=0.35  ✓
node-2 → node-3 (0.5): rising=0.263  expected=0.25  ✓
node-3 → node-4 (0.3): rising=0.139  expected=0.15  ✓
```

4 breeders, 12 pairs evaluated, 3 edges detected, 0 false positives.

## What Was Fixed This Session

### Infrastructure (6 layers, each masking the next)
1. `SimpleLogRecordProcessor` import from wrong module → breeders crashed on startup (breeder 0.137.0)
2. No stdout handler → Windmill job_logs empty (breeder 0.138.0)
3. `allow_structured_metadata: false` → Loki silently dropped OTLP logs (chart fix)
4. Invalid `otlp_config` fields → Loki crash loop (chart fix)
5. `memberlist` DNS lookup → Loki couldn't form ring (configmap patch)
6. `frontend.scheduler_address: ""` → query path couldn't reach ingester (chart PR #218)

### Coordinator bugs
7. Stale lease `_has_active_sender()` OR logic → dead senders blocked all receivers (breeder 0.140.0)
8. Resume-budget: in-memory `_push_count`/`_pause_count` reset on worker restart but lease DB retained state → infinite pause loop (breeder 0.141.0)

### CFAR detection bugs
9. Push/pause timestamps not sorted → inverted windows (causal 0.3.4)
10. Baseline filtered by `phase == "pause"` label → unreliable (causal 0.3.5)
11. Push window overlapped pause window → contaminated samples (causal 0.3.6)
12. Majority voting → replaced with confidence-based detection (causal 0.3.7)

### Workflow bugs
13. Stale `/tmp/bench-generic/topology.yaml` directory from Jul 27 → Docker mount failed
14. NixOS container has no `/tmp`, no root in passwd → docker create + cp + `--user 0:0`
15. Duplicate breeder on node-2 → race in retry loop → purge by name pattern (PR #288)

## Versions Deployed

- breeder: 0.141.0
- causal: 0.3.7
- chart: includes Loki config fix, breeder 0.141.0, causal 0.3.7

## What Works

- OTLP→Loki: FULLY WORKING (breeder logs with structured metadata in Loki)
- Coordinator cycling: PROVEN (push/pause/hold turn-taking with fencing tokens)
- CFAR detection: PROVEN (pair test conf=1.0, chain4 all 3 edges)
- Composition: VALIDATED (3 edges at correct strengths, topology recovered exactly)
- Bench-generic: WORKS (4 nodes, linear coupling, configurable topology)

## Next Steps — Validation Sweep

See: `/projects/godon/docs/validation-sweep.md`

Priority order:
1. Linear pair sweep (coupling strength × noise grid) — detection sensitivity curve
2. Diamond topology (branching + merge) — non-chain generalization
3. One nonlinear coupling shape — boundary of method
4. Composition prediction — do chained edges predict distant-node response?

## Known Technical Debt

- `_CachedStorage` shutdown check still broken (non-fatal)
- HOLD_CALIB skipped when hold_params from config (never tested with auto-calibration)
- Characterization limited to step amplitude (no full response curve)
- Coordinator robustness: 3 bugs fixed this session, likely more at scale
- Windmill as execution engine: unresolved design question
- Hardcoded thresholds: STALE_SENDER_MULTIPLIER, WORST_CASE_TRIAL_SECONDS, CFAR min cells

## Paper Plan

Title candidates: "Active Coupling Discovery" or "The Ripple Protocol"
- Paper 2: The measurement protocol (this session's work is the validation)
- Paper 3: Composition prediction + causal model

## Key Files

- `/projects/godon/docs/validation-sweep.md` — sweep strategy and experiment matrix
- `/projects/godon-breeders/engine/detection_coordinator.py` — coordinator with all fixes
- `/projects/godon-images/images/godon-causal/src/detector.rs` — CFAR detector with all fixes
- `/projects/godon-charts/charts/godon-observability/values.yaml` — Loki config (allow_structured_metadata, frontend scheduler)
- `/projects/godon-charts/charts/godon/values.yaml` — BREEDER_VERSION=0.141.0, causal tag=0.3.7
- `/projects/godon/.github/workflows/bench-chain4.yml` — chain4 workflow (docker cp, user 0:0, purge duplicates)

## Access

- SSH: `ssh -i /projects/godon/openstack godon@140.211.166.29`
- KUBECONFIG: `/tmp/kind_kubeconfig.yaml`
- GitHub token: `/tmp/gh_token.txt` (regenerate via `/tmp/ghenv/bin/python /tmp/get_token.py`)
- Test venv: `/tmp/breeder-test-venv` (Python 3.11, pytest + optuna + scipy)

## Repos — All On Main, Zero Open PRs

- godon: chain4 workflow + topology mount fixes
- godon-breeders: 0.141.0 (resume-budget fix)
- godon-charts: Loki config fix, breeder 0.141.0, causal 0.3.7
- godon-images: causal 0.3.7 (CFAR fixes)
- godon-controller: clean
