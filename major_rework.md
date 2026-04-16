# Godon Configuration v0.2 → v0.3 Major Rework

**Date:** 2025-01-12
**Config Version:** 0.2 → 0.3
**Status:** Design complete, implementation in progress

## Executive Summary

This rework introduces **guardrails with automatic rollback** and expands **Linux tuning support** beyond sysctl to include sysfs, cpufreq, and ethtool parameters. The configuration structure has been simplified by removing redundant `type` fields (the breeder now infers types from an internal registry) and standardizing constraint terminology.

**Key Changes:**
- ✅ Added `guardrails` section for safety limits with automatic rollback
- ✅ Added `rollback_strategies` section for reusable recovery configurations
- ✅ Supported sysfs, cpufreq, ethtool parameter categories
- ✅ Removed `type` fields from parameters (breeder knows types internally)
- ✅ Changed `enum` → `values` for better terminology
- ✅ Standardized all ranges under `constraints` list
- ✅ Changed `allows_reboot` → `allows_downtime` (universal across breeder types)

**Motivation:** Production-safe system optimization requires safety mechanisms. If optimization pushes system CPU to 95%, we should rollback even if RTT improved. Objectives define what we optimize (Pareto frontier), guardrails define safety limits (binary rollback trigger).

---

## Configuration Changes

### 1. Removed `type` Field from Parameters

**Before (v0.2):**
```yaml
settings:
  sysctl:
    net.ipv4.tcp_rmem:
      type: "suggest_int"  # REDUNDANT - breeder already knows this
      constraints:
        - {lower: 4096, upper: 131072}
```

**After (v0.3):**
```yaml
settings:
  sysctl:
    net.ipv4.tcp_rmem:
      constraints:
        - {step: 100, lower: 4096, upper: 131072}
```

**Rationale:** The breeder maintains an internal parameter registry. It knows `net.ipv4.tcp_rmem` is an integer parameter. Requiring `type` in the config is redundant and error-prone.

**Implementation:** Breeder must implement parameter type registry mapping parameter names → types.

---

### 2. Changed `enum` → `values`

**Before (v0.2):**
```yaml
settings:
  sysctl:
    net.ipv4.tcp_congestion_control:
      type: "suggest_categorical"
      enum: ["cubic", "bbr", "reno"]
```

**After (v0.3):**
```yaml
settings:
  sysctl:
    net.ipv4.tcp_congestion_control:
      constraints:
        values: ["cubic", "bbr", "reno"]
```

**Rationale:** `enum` is programming terminology. `values` is more user-friendly and semantically clear.

---

### 3. All Ranges Under `constraints` List

**Before (v0.2):**
```yaml
settings:
  sysctl:
    net.ipv4.tcp_rmem:
      type: "suggest_int"
      lower: 4096
      upper: 131072
```

**After (v0.3):**
```yaml
settings:
  sysctl:
    net.ipv4.tcp_rmem:
      constraints:
        - {step: 100, lower: 4096, upper: 131072}
        - {step: 100, lower: 262144, upper: 6291456}  # Multiple disjoint ranges
```

**Rationale:** List structure supports multiple disjoint ranges. Parallel workers can explore different regions simultaneously (e.g., conservative 4K-128K vs performance 256K-6M).

---

### 4. New Settings Categories: sysfs, cpufreq, ethtool

**v0.2 only supported sysctl. v0.3 adds:**

```yaml
settings:
  # sysfs (filesystem paths)
  sysfs:
    cpu_governor:
      path: "/devices/system/cpu/cpu0/cpufreq/scaling_governor"
      constraints:
        values: ["performance", "powersave", "ondemand"]

    transparent_hugepage:
      path: "/sys/kernel/mm/transparent_hugepage/enabled"
      constraints:
        values: ["always", "madvise", "never"]

  # CPU frequency scaling
  cpufreq:
    governor:
      constraints:
        values: ["performance", "powersave", "ondemand", "schedutil"]

    min_freq_ghz:
      constraints:
        - {step: 0.2, lower: 1.2, upper: 2.4}

    max_freq_ghz:
      constraints:
        - {step: 0.2, lower: 2.4, upper: 4.8}

  # Network interface settings
  ethtool:
    eth0:
      tso:
        constraints:
          values: ["on", "off"]

      rx_ring:
        constraints:
          - {step: 512, lower: 512, upper: 8192}
```

**Rationale:** Linux performance tuning requires multiple mechanisms. Structured approach (separate categories) balances clarity vs complexity.

---

### 5. Added `guardrails` Section

**NEW in v0.3:**
```yaml
guardrails:
  - name: "cpu_usage"
    hard_limit: 90  # Rollback if CPU usage exceeds 90%
    reconnaissance:
      service: prometheus
      query: "avg(rate(process_cpu_seconds_total[5m])) * 100"
      stabilization_seconds: 10
      samples: 3
      interval: 2

  - name: "system_errors"
    hard_limit: 10  # Rollback if system errors exceed 10 per minute
    reconnaissance:
      service: prometheus
      query: "rate(kernel_errors_total[1m])"
      stabilization_seconds: 10
      samples: 3
      interval: 2
```

**Critical Concept: Guardrails vs Objectives**

- **Objectives:** What we optimize (multi-objective Pareto optimization). Tradeoffs allowed.
  - Example: Minimize RTT while maximizing throughput
  - If RTT improves but throughput degrades slightly, trial may stay on Pareto frontier

- **Guardrails:** Safety limits (binary rollback trigger). No tradeoffs.
  - Example: CPU must stay below 90%
  - If RTT improves but CPU hits 95%, we **ROLLBACK** immediately
  - System safety > optimization performance

**Key Difference:** Objectives use Optuna's multi-objective optimization. Guardrails trigger controller's rollback logic.

---

### 6. Added `rollback_strategies` Section

**NEW in v0.3:**
```yaml
rollback_strategies:
  standard:
    consecutive_failures: 3  # Avoid false positives from transient spikes
    target_state: "previous"  # previous | best | baseline
    max_attempts: 3
    on_failure: "stop"  # stop | continue | skip_target
    timeout_seconds: 60
    after:
      action: "pause"  # pause | continue | stop
      duration: 300  # Required if action=pause

  aggressive:
    consecutive_failures: 1
    target_state: "baseline"
    max_attempts: 1
    on_failure: "skip_target"
    timeout_seconds: 30
    after:
      action: "continue"
```

**Referenced by targets:**
```yaml
effectuation:
  targets:
    - type: "ssh"
      id: "target_1"
      address: "10.0.5.53"
      rollback:
        enabled: true
        strategy: "standard"  # References rollback_strategies.standard
```

**Rationale:** Multiple targets often share rollback behavior. Define once, reference multiple times.

---

### 7. Changed `allows_reboot` → `allows_downtime`

**Before (v0.2):**
```yaml
effectuation:
  targets:
    - allows_reboot: false  # Linux-specific terminology
```

**After (v0.3):**
```yaml
effectuation:
  targets:
    - allows_downtime: false  # Universal across all breeder types
```

**Rationale:** Different breeder types have different failure modes. Kubernetes pods restart. Linux systems reboot. Database clusters failover. "Downtime" is universal.

**Important:** `allows_downtime` does NOT affect rollback logic. Rollback always happens if guardrails violated. `allows_downtime` is metadata for the breeder's effectuation logic (e.g., skip tuning params that require reboot if downtime not allowed).

---

### 8. Added `skip_target` Option

**NEW in v0.3:**
```yaml
rollback_strategies:
  multi_target:
    on_failure: "skip_target"  # NEW: Mark failed target unhealthy, continue with others
```

**Use Case:** Multi-target scenarios. If target_1 fails rollback after 3 attempts, mark it unhealthy and continue optimizing target_2, target_3, etc.

**Other options:** `stop` (halt entire optimization run), `continue` (keep trying with failed target - likely fails again).

---

## Validation Rules (Implementation Requirements)

### Controller Validation (Phase 1)

**File:** `/home/matthias/Projects/godon-controller/controller/breeder_create.py`

1. **Validate constraint structure:**
   - All constraints must be a list (even single range)
   - Each constraint must have either:
     - Integer ranges: `step`, `lower`, `upper` (all required)
     - Categorical values: `values` (array of strings, min 2 items)

2. **Validate constraint type matching:**
   - Integer parameters: must have list of ranges (NOT `values`)
   - Categorical parameters: must have `values` (NOT ranges)
   - Controller must know parameter types (need type registry or API call to breeder)

3. **Validate guardrails section (if present):**
   - Each guardrail must have:
     - `name` (string, non-empty)
     - `hard_limit` (number, direction inferred from parameter semantics)
     - `reconnaissance` section with:
       - `service` (must be "prometheus" or supported service)
       - `query` (string, valid query for service)
       - `stabilization_seconds` (integer >= 0)
       - `samples` (integer >= 1)
       - `interval` (integer >= 1)

4. **Validate rollback_strategies section (if present):**
   - Each strategy must have:
     - `consecutive_failures` (integer >= 1)
     - `target_state` (one of: "previous", "best", "baseline")
     - `max_attempts` (integer >= 1)
     - `on_failure` (one of: "stop", "continue", "skip_target")
     - `timeout_seconds` (integer >= 1)
     - `after` section with:
       - `action` (one of: "pause", "continue", "stop")
       - `duration` (required if action="pause", integer >= 1)

5. **Validate rollback strategy references:**
   - If `rollback.strategy` is specified in target, it must exist in `rollback_strategies`
   - If `rollback.enabled=true`, strategy must be specified

6. **Validate allows_downtime vs reboot-required settings:**
   - This is a WARNING, not a hard validation error
   - If `allows_downtime=false`, warn if config includes parameters that require reboot
   - Controller needs to know which parameters require reboot (from breeder metadata)

7. **Support new settings categories:**
   - Accept `sysfs`, `cpufreq`, `ethtool` in addition to `sysctl`
   - Validate structure matches documented format
   - Pass through to breeder (controller doesn't need deep knowledge)

8. **Update config sharding for new constraint structure:**
   - Current code expects single `lower`/`upper` (v0.2)
   - Update to support list of constraints (v0.3)
   - Assign disjoint ranges to different workers for parallel exploration

---

### Breeder Parameter Registry (Phase 2)

**File:** `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`

**Create internal registry:**
```python
PARAMETER_REGISTRY = {
    "net.ipv4.tcp_rmem": {
        "type": "int",
        "requires_reboot": False,
    },
    "net.ipv4.tcp_congestion_control": {
        "type": "categorical",
        "requires_reboot": False,
    },
    "cpu_governor": {
        "type": "categorical",
        "requires_reboot": False,
        "path": "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    },
    # ... all supported parameters
}
```

**Implement type inference:**
```python
def get_parameter_type(param_name):
    if param_name not in PARAMETER_REGISTRY:
        raise ValueError(f"Unknown parameter: {param_name}")
    return PARAMETER_REGISTRY[param_name]["type"]
```

---

### Breeder Suggestion Logic (Phase 3)

**File:** `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`

**Current implementation (v0.2):**
```python
# Line 347: Hardcoded to sysctl only
for param_name, constraints in shard['settings']['sysctl'].items():
    # Line 352-353: Single range only
    lower = constraints['lower']
    upper = constraints['upper']
    # Line 355: Only supports suggest_int
    trial.suggest_int(param_name, lower, upper)
```

**Required updates (v0.3):**

1. **Support multiple settings categories:**
   ```python
   for category in ['sysctl', 'sysfs', 'cpufreq', 'ethtool']:
       if category in shard['settings']:
           for param_name, constraints in shard['settings'][category].items():
               # ... handle each parameter
   ```

2. **Support multiple disjoint ranges:**
   ```python
   # constraints is now a list
   for constraint in constraints['constraints']:
       if 'values' in constraint:
           # Categorical
           trial.suggest_categorical(param_name, constraint['values'])
       else:
           # Integer range with step
           trial.suggest_float(param_name, constraint['lower'], constraint['upper'], step=constraint['step'])
   ```

3. **Support categorical parameters:**
   ```python
   if 'values' in constraint:
       trial.suggest_categorical(param_name, constraint['values'])
   ```

---

### Guardrails & Rollback (Phase 4)

**File:** `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`

**New logic required:**

1. **Check guardrails after each trial:**
   ```python
   def objective(trial):
       # ... apply parameters
       # ... wait for stabilization
       # ... collect metrics

       # Check guardrails
       for guardrail in config['guardrails']:
           value = query_metric(guardrail['reconnaissance'])
           if exceeds_limit(value, guardrail['hard_limit']):
               return FAILED_TRIAL_VALUE  # Tell Optuna this trial failed

       # Return objectives for Pareto optimization
       return [rtt, throughput]
   ```

2. **Implement rollback logic:**
   - Controller monitors trial completion
   - If trial fails guardrail check, trigger rollback
   - Rollback strategy determines:
     - Which state to restore (previous/best/baseline)
     - How many consecutive failures before giving up
     - What to do if rollback fails (stop/continue/skip_target)
     - What to do after successful rollback (pause/continue/stop)

3. **Handle consecutive_failures:**
   - Track consecutive failures per target
   - Only rollback after N consecutive failures (avoid false positives)
   - Reset counter on successful trial

4. **Implement skip_target:**
   - Mark target as unhealthy in controller metadata
   - Exclude from future trials
   - Continue with other targets

---

## Design Decisions & Trade-offs

### 1. Objectives vs Guardrails Separation

**Decision:** Rollback ONLY triggered by guardrails, not objective degradation.

**Trade-off:**
- ✅ **Pro:** Clear separation of concerns (optimization vs safety)
- ✅ **Pro:** Multi-objective optimization handled by Optuna (Pareto frontier)
- ✅ **Pro:** Safety limits never violated by design
- ❌ **Con:** Complex to explain to users (objectives don't trigger rollback)
- ❌ **Con:** Users might expect rollback on objective degradation

**Alternatives considered:**
1. Dual-objective guardrails (rollback if metric degrades AND exceeds threshold)
   - Rejected: Too complex for v0.3
   - Could add in future version

2. Rollback on any objective degradation
   - Rejected: Breaks Pareto optimization (tradeoffs are fundamental)
   - Example: Low latency often requires higher CPU cost

---

### 2. Type Field Removal

**Decision:** Remove `type` field from parameters, infer from internal registry.

**Trade-off:**
- ✅ **Pro:** Cleaner config (less redundancy)
- ✅ **Pro:** Single source of truth (breeder registry)
- ✅ **Pro:** Can add new parameters without config changes
- ❌ **Con:** Less self-documenting (can't see type in config)
- ❌ **Con:** Breeder must maintain comprehensive registry

**Alternatives considered:**
1. Keep `type` field but make it optional
   - Rejected: Ambiguous (when required vs optional?)

2. Use `type` field for override only
   - Rejected: Adds complexity (override logic)

---

### 3. Multiple Disjoint Ranges

**Decision:** Support list of constraints, each with separate ranges.

**Trade-off:**
- ✅ **Pro:** Parallel workers can explore different regions
- ✅ **Pro:** Can specify conservative vs aggressive ranges
- ✅ **Pro:** Accelerates discovery of optimal configurations
- ❌ **Con:** More complex config structure
- ❌ **Con:** Harder to shard across workers

**Alternatives considered:**
1. Single continuous range only
   - Rejected: Limits exploration flexibility

2. Named ranges with explicit worker assignment
   - Rejected: Too complex for v0.3

---

### 4. Guardrails Without Direction

**Decision:** `hard_limit` is a single number, direction inferred from parameter semantics.

**Trade-off:**
- ✅ **Pro:** Simpler config (no `min`/`max` confusion)
- ✅ **Pro:** Works for metrics where direction is obvious (CPU, errors, latency)
- ❌ **Con:** Ambiguous for metrics like "cache_hit_ratio" (higher is better... or is it?)
- ❌ **Con:** Requires breeder to know semantics

**Alternatives considered:**
1. Explicit `min_limit` and `max_limit`
   - Rejected: Most use cases only need one direction

2. Require direction in config: `direction: "must_not_exceed"`
   - Rejected: Verbose, can infer from parameter name

---

### 5. Rollback Strategy Reusability

**Decision:** Define strategies in `rollback_strategies`, reference by name.

**Trade-off:**
- ✅ **Pro:** DRY (define once, use multiple times)
- ✅ **Pro:** Easier to update (change in one place)
- ✅ **Pro:** Clear naming (strategy names document intent)
- ❌ **Con:** Indirection (must lookup strategy definition)
- ❌ **Con:** More complex config structure

**Alternatives considered:**
1. Inline rollback config in each target
   - Rejected: Violates DRY, error-prone

2. Use YAML anchors and aliases
   - Rejected: Less discoverable, harder to validate

---

## Implementation Phases

### Phase 1: Controller Validation
**Status:** Ready to start
**Files:**
- `/home/matthias/Projects/godon-controller/controller/breeder_create.py`
- `/home/matthias/Projects/godon-controller/controller/breeder_service.py`

**Tasks:**
- [ ] Validate new constraint structure (list of ranges)
- [ ] Validate constraint type matching (int = ranges, categorical = values)
- [ ] Validate guardrails section
- [ ] Validate rollback_strategies section and references
- [ ] Validate allows_downtime vs reboot-required settings
- [ ] Support sysfs, cpufreq, ethtool settings categories
- [ ] Update config sharding for new constraint structure

---

### Phase 2: Breeder Parameter Registry
**Status:** Blocked by Phase 1
**Files:**
- `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`

**Tasks:**
- [ ] Create internal parameter registry
- [ ] Support type inference from registry
- [ ] Add metadata (requires_reboot, path, etc.)
- [ ] Document all supported parameters

---

### Phase 3: Breeder Suggestion Logic
**Status:** Blocked by Phase 2
**Files:**
- `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`

**Tasks:**
- [ ] Support multiple disjoint ranges
- [ ] Support categorical parameters
- [ ] Support sysfs, cpufreq, ethtool categories
- [ ] Update trial.suggest_* calls

---

### Phase 4: Guardrails & Rollback
**Status:** Blocked by Phase 3
**Files:**
- `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`
- `/home/matthias/Projects/godon-controller/controller/*` (rollback orchestration)

**Tasks:**
- [ ] Check guardrails after each trial
- [ ] Implement rollback logic in controller
- [ ] Handle consecutive_failures counter
- [ ] Implement skip_target logic
- [ ] Add rollback state persistence (previous/best/baseline)

---

## Migration Path for Users

### Upgrading from v0.2 to v0.3

**1. Update configVersion:**
```yaml
meta:
  configVersion: "0.3"
```

**2. Remove type fields:**
```yaml
# BEFORE
settings:
  sysctl:
    net.ipv4.tcp_rmem:
      type: "suggest_int"  # REMOVE THIS
      constraints:
        - {lower: 4096, upper: 131072}

# AFTER
settings:
  sysctl:
    net.ipv4.tcp_rmem:
      constraints:
        - {step: 100, lower: 4096, upper: 131072}
```

**3. Replace enum with values:**
```yaml
# BEFORE
enum: ["cubic", "bbr"]

# AFTER
constraints:
  values: ["cubic", "bbr"]
```

**4. Add guardrails (optional but recommended):**
```yaml
guardrails:
  - name: "cpu_usage"
    hard_limit: 90
    reconnaissance:
      service: prometheus
      query: "avg(rate(process_cpu_seconds_total[5m])) * 100"
      stabilization_seconds: 10
      samples: 3
      interval: 2
```

**5. Add rollback_strategies (optional but recommended):**
```yaml
rollback_strategies:
  standard:
    consecutive_failures: 3
    target_state: "previous"
    max_attempts: 3
    on_failure: "stop"
    timeout_seconds: 60
    after:
      action: "pause"
      duration: 300
```

**6. Reference rollback strategy in targets:**
```yaml
effectuation:
  targets:
    - rollback:
        enabled: true
        strategy: "standard"  # ADD THIS
```

**7. Change allows_reboot to allows_downtime:**
```yaml
# BEFORE
allows_reboot: false

# AFTER
allows_downtime: false
```

---

## Testing Checklist

### Unit Tests

- [ ] Controller validates new constraint structure
- [ ] Controller validates constraint type matching
- [ ] Controller validates guardrails section
- [ ] Controller validates rollback_strategies section
- [ ] Controller validates strategy references
- [ ] Breeder parameter registry returns correct types
- [ ] Breeder handles multiple disjoint ranges
- [ ] Breeder handles categorical parameters
- [ ] Breeder handles sysfs parameters
- [ ] Breeder handles cpufreq parameters
- [ ] Breeder handles ethtool parameters

### Integration Tests

- [ ] End-to-end: Create breeder with v0.3 config
- [ ] End-to-end: Guardrail violation triggers rollback
- [ ] End-to-end: Consecutive failures counter works
- [ ] End-to-end: Rollback to previous/best/baseline states
- [ ] End-to-end: skip_target marks unhealthy, continues
- [ ] End-to-end: Multi-objective Pareto optimization still works
- [ ] End-to-end: Parallel workers explore disjoint ranges

### Smoke Tests

- [ ] Deploy with example `/home/matthias/Projects/godon/examples/network.yml`
- [ ] Run 10 trials without guardrail violations
- [ ] Trigger guardrail violation, verify rollback
- [ ] Verify multi-objective optimization (RTT + throughput)
- [ ] Verify parallel worker exploration

---

## Open Questions

1. **Parameter type registry location:**
   - Should registry be in breeder only?
   - Or should controller have read-only access for validation?
   - **Decision:** Breeder only initially, can add API endpoint later

2. **Guardrail direction inference:**
   - How does breeder know if CPU usage should be `< 90` or `> 10`?
   - **Decision:** Hardcoded logic for common metrics (CPU, errors, latency = must not exceed)

3. **Rollback state persistence:**
   - Where to store "previous", "best", "baseline" states?
   - **Decision:** Controller metadata database (same as trial history)

4. **Partial rollback:**
   - If multiple targets, do we rollback all or just failed target?
   - **Decision:** Only failed target (others may be safe)

---

## References

- **Example v0.3 config:** `/home/matthias/Projects/godon/examples/network.yml`
- **Controller entry point:** `/home/matthias/Projects/godon-controller/controller/breeder_create.py`
- **Breeder worker:** `/home/matthias/Projects/godon-breeders/linux_performance/breeder_worker.py`
- **Controller service:** `/home/matthias/Projects/godon-controller/controller/breeder_service.py`
- **API handlers:** `/home/matthias/Projects/godon-images/images/godon-api/src/handlers.nim`

---

## Git Commit Message

```
feat: Add guardrails with automatic rollback and expand Linux tuning support

This major rework introduces safety mechanisms and broader parameter support
to the godon configuration format (v0.2 → v0.3).

BREAKING CHANGES:
- Removed 'type' field from parameters (breeder infers from internal registry)
- Changed 'enum' to 'values' for categorical parameters
- Standardized all ranges under 'constraints' list
- Changed 'allows_reboot' to 'allows_downtime' (universal terminology)

NEW FEATURES:
- Added 'guardrails' section for safety limits with automatic rollback
- Added 'rollback_strategies' section for reusable recovery configurations
- Supported sysfs, cpufreq, ethtool parameter categories
- Added 'skip_target' rollback failure option for multi-target scenarios
- Supported multiple disjoint ranges for parallel worker exploration

DESIGN NOTES:
- Objectives: Multi-objective Pareto optimization (tradeoffs allowed)
- Guardrails: Binary safety limits (rollback immediately if exceeded)
- Rollback ONLY triggered by guardrails, not objective degradation
- Config version bumped to 0.3

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**Next Steps:** Start Phase 1 (Controller Validation)
