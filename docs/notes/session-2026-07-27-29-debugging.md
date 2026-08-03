# Session Notes — July 27-29, 2026

## SHIPPED

### Coordinator fix (breeder 0.135.0)
- `detection_coordinator.py`: count-based budget replaces time-based lease. No more lease expiry on variable-length trials.
- `detection_coordinator.py`: readiness barrier skipped entirely when hold_params from config. Fixes handover desync.
- `detection_coordinator.py`: introspective logging for PUSH/PAUSE entry, receiver HOLD periodic state.
- `otel_logging.py`: `SimpleLogRecordProcessor` replaces `BatchLogRecordProcessor`. Batch was losing logs because Windmill runs each flow step as a short-lived subprocess — the batch never flushes before exit. Simple exports synchronously on every log call.
- `otel_logging.py`: `init_telemetry()` wrapped in try/except. `trace.set_tracer_provider()` throws if Windmill already set one — this was preventing the logger provider from initializing, silently killing ALL OTLP logging.
- Tagged as bare `0.135.0` (NOT prefixed — seeder checks out bare tag).
- component.yaml added for bench_generic strain (was missing — seeder couldn't discover the strain).

### Generic bench (godon-bench-generic 0.1.0)
- Configurable synthetic coupling bench with known ground truth.
- Accepts named params (`{"param_0": 50.0}`) — matches greenhouse pattern.
- Returns named scalar objectives (`{"objective_0": 0.3}`) — dynamic count from topology config.
- Base functions: linear, polynomial, threshold, saturation.
- Noise: stacked gaussian + colored + drift. All independently configurable, all default to trivial.
- Edge drift: per-edge drift_rate for state-dependent coupling.
- Cross-parameter interactions: configurable multiplicative bundles.
- GHCR image built and tagged.

### Bench workflow (bench-generic.yml)
- Parameterized: coupling_strength, base_function, noise_gaussian, noise_colored, min_trials, max_wait.
- Purge stale breeders step (prevents orphaned breeders from cancelled runs).
- Uses jq instead of python3 (NixOS runner doesn't have python3 in PATH).
- Mounts topology directory instead of file (Docker creates directory if file mount path doesn't exist).
- Breeder config in work dir, not /tmp (CLI runs inside docker container with different mount).

### Chart versions (godon-charts)
- breeder: 0.135.0
- observer: 0.70.0 (causal proxy endpoints)
- controller: 0.50.0
- causal: 0.1.0

### Roadmap
- `/projects/godon/docs/notes/causal-roadmap.md` — full architecture, method, milestones, tractability, Markov blanket, self-diagnosis, optimization value scaling, Pareto, high-dimensional handling.

## VALIDATED

### Bench ran successfully (07:11 UTC, July 29)
- 221/204 trials over 12 minutes.
- Coordinator activated: optimize → hold → push/pause confirmed via trial user_attrs (coord_state, lease_phase).
- Both breeders ran the full distance.
- Ground truth config loaded: node-1 → node-2 at 0.7, linear, gaussian 0.02.

### OTLP logging pipeline works
- Collector receives OTLP logs on 4318.
- Exports to Loki at 3100/otlp via otlphttp exporter.
- Loki 3.0.0 accepts OTLP natively.
- Breeder logs (reconnaissance, effectuation, watermark, breeder_worker scopes) confirmed in Loki during a run with 0.134.0 (before the SimpleLogRecordProcessor fix was deployed — those logs came from the error-handling fix catching the tracer provider conflict).
- `SimpleLogRecordProcessor` confirmed in Windmill DB for 0.135.0.

## KNOWN ISSUES (blocking)

### 1. Windmill job dispatch — breeder jobs tagged as `default` not `breeder`
After repeated reinstalls, the controller dispatches breeder optimization jobs with tag `default` instead of tag `breeder`. The breeder workers (tagged `breeder`) never pick them up. Only the default workers see them, and they don't have the breeder Python deps.

This worked at 07:11 UTC. The repeated reinstalls likely corrupted Windmill's worker group routing. Needs investigation in `f/controller/breeder_start` or the controller's job dispatch logic.

**Fix path:** Fresh reinstall, single bench run. If it recurs, check the controller's `breeder_start` Windmill script for how it sets the worker tag.

### 2. Coordinator 140-second stall
During the 200-trial run, both breeders stalled at 116 trials from ~320s to ~460s (140 seconds). Then resumed. Coordinator eventually recovered and continued past 200.

Likely a lease/budget race during handover. The count-based budget fix improved things (recovery happened) but didn't fully eliminate the stall.

**Needs:** Loki logs from the coordinator during the stall. The `SimpleLogRecordProcessor` fix should make those visible once dispatch works.

### 3. Breeder 2 reconnaissance URL not replaced
The workflow's sed replaces `http://bench-generic:8090/node-1` with the KIND IP. Breeder 1 gets the correct IP. Breeder 2 still shows `http://bench-generic:8090/node-2` — the sed pattern may not match the reconnaissance section in breeder-2.yml.

### 4. Breeder worker error: `'Study' object has no attribute 'storage'`
Seen in Loki logs: "Failed to check shutdown flag: 'Study' object has no attribute 'storage'". Non-fatal but indicates a version mismatch between the breeder worker code and Optuna API.

## KEY LEARNINGS

1. **Bare tags only on godon-breeders.** The seeder does `git checkout "0.135.0"`. Prefixed tags (`godon-breeders-0.135.0`) don't work. Always create bare tag. Never force-push tags.

2. **component.yaml required for seeder discovery.** Each strain needs `strains/<name>/component.yaml` or the seeder never finds it.

3. **Rollback config requires `after` and `timeout_seconds` fields.** Controller validation (since 0.16.0, January 2026) enforces this. Missing fields = config rejected.

4. **Windmill runs each flow step as separate subprocess.** `BatchLogRecordProcessor` loses logs because the process exits before flush. `SimpleLogRecordProcessor` exports synchronously.

5. **`trace.set_tracer_provider()` throws if already set.** Windmill sets its own. Must catch this exception or the logger provider never initializes — silently killing ALL OTLP logging.

6. **NixOS runner: no python3 in PATH.** Use jq in workflows, not python3.

7. **Docker volume mounts: mount directory, not file.** If the file doesn't exist before mount, Docker creates a directory at the path.

## SSH ACCESS
`ssh -i /projects/godon/openstack godon@140.211.166.29`
Kubeconfig: `/tmp/kind_kubeconfig.yaml`
GitHub token: `/tmp/get_token.py` → `/tmp/gh_token.txt` (regenerate with `/tmp/ghenv/bin/python /tmp/get_token.py`)

## NEXT STEPS (in order)

1. ~~Fresh reinstall + single bench run~~ — reinstall triggered with breeder 0.136.0 (Jul 29 15:10 UTC).
2. If trials flow → query Loki for coordinator logs → debug 140s stall.
3. ~~If trials don't flow → check controller's `breeder_start` Windmill script~~ — NOT a code bug; engine/component.yaml correctly sets `tag: "breeder"`. Controller relies on deployed script's tag. Clean reinstall should fix corrupted Windmill routing state.
4. ~~Fix breeder 2 URL sed in workflow~~ — FIXED: real bug was in `create_target` sed (only had node-1 pattern). godon PR #276 merged.
5. Test causal `/build` against real detection data.
6. Run composition test (chain4 topology, 0.7 × 0.5 × 0.3 = 0.105 expected).

## JUL 29-30 SESSION — MASSIVE PROGRESS

### Infrastructure fixed (6 layers of OTLP/Loki, each masking the next):
- SimpleLogRecordProcessor imported from wrong module (opentelemetry.sdk._logs vs .export) → breeder 0.137.0
- Stdout StreamHandler added to get_logger for Windmill job_logs → breeder 0.138.0
- Loki allow_structured_metadata: true → chart PR #215
- Loki memberlist DNS removal + frontend scheduler_address localhost:9095 → chart PR #218
- Causal list_breeders from pg_database instead of studies table → causal 0.2.0
- CFAR baseline from pause-phase trials instead of hold_calib → causal 0.3.0

### Breeder fixes:
- Stale lease fix: _has_active_sender() heartbeat-only, not OR(budget,heartbeat) → breeder 0.140.0
- Coordinator OTLP logging: get_logger instead of logging.getLogger → breeder 0.136.0
- SQLAlchemy 2.0 shutdown check: study._storage.engine → breeder 0.136.0
- Integration tests rewritten for count-based budget → breeder 0.136.0

### PROVEN:
- Breeder runs work: 200+ trials, effectuation succeeds, coordinator cycles
- Coordinator choreography: OPTIMIZE → HOLD_CALIB → IMPULSE_CALIB → PUSH(15) → PAUSE(15) → DONE → COOLDOWN → OPTIMIZE with turn-taking (verified in Loki)
- CFAR detection: 0.95 confidence on first /build call (before list_breeders fix broke it)
- OTLP → Loki: breeder Python logs flowing with structured metadata (scope, file, line, service_instance_id)
- 140s stall: NOT observed in latest 200-trial run (stale lease fix resolved it)
- Generic bench speed: 2-3s per trial, 200-trial run in ~12 minutes

### REMAINING (next session):
1. Reinstall with causal 0.3.0 + breeder 0.140.0
2. Run bench, call /build, verify detected edges in /graph
3. Fix _CachedStorage shutdown warning (needs _storage._backend.engine unwrap)
4. Test nonlinear base functions
5. Composition test (chain4, 0.7 × 0.5 × 0.3 = 0.105)
6. Persist Loki config (chart PR #218 merged)

## FIXES SHIPPED (breeder 0.136.0, Jul 29 15:00 UTC)

### 1. Coordinator OTLP logging (PR #172)
- `detection_coordinator.py`: `logging.getLogger(__name__)` → `get_logger(__name__)` from `otel_logging`.
- Root cause: coordinator used standard Python logging (no OTLP handler). All other modules (breeder_worker, reconnaissance, effectuation, watermark) used `get_logger()` which attaches the OTLP LoggingHandler. That's why coordinator scope was invisible in Loki.
- This unblocks coordinator choreography debugging via Loki.

### 2. SQLAlchemy 2.0 shutdown check (PR #172)
- `breeder_worker.py` line 864: `self.study.storage._engine.execute(query)` → `self.study._storage.engine.connect()` + `text()`.
- Three layered API breaks: `.storage` → `._storage`, `._engine` → `.engine`, `.execute()` → `text()` + `.connect()`.
- Non-fatal but silently broke graceful shutdown.

### 3. Bench-generic node-2 URL (godon PR #276)
- `.github/workflows/bench-generic.yml`: `create_target` step only had `node-1` sed pattern. Added `node-2`.
- The reported symptom (breeder 2 URL not replaced) was actually from the target config, not the breeder recon block (which was already correct).

### 4. Integration tests rewritten (PR #172)
- Old tests referenced `WARMUP`, `SENDER_PUSH`, `RECEIVER_HOLD`, `detection_rounds` table — all removed in coordinator refactor.
- New tests: push completes with all FAILs, guardrail fail no-op during push, escape hatches for all states, full sender round (PUSH→PAUSE→COOLDOWN→OPTIMIZE), optimize gating.
- All 262 tests pass (256 unit + 6 integration).
