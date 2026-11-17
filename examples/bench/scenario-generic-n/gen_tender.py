#!/usr/bin/env python3
"""gen_tender.py — one SILENT-precision tender config for the generic N-room.

Precision is deliberately NOT declared (the estate's settings tree carries it,
frozen at spawn) — a convergence_threshold line here would be refused at worker
init since 0.187.5. Dependency-free on purpose.
"""
import argparse

p = argparse.ArgumentParser()
p.add_argument("--recon-url", required=True)
p.add_argument("--target-id", required=True)
p.add_argument("--group", default="bench-generic-n")
p.add_argument("--push", default="6")
p.add_argument("--pause", default="6")
a = p.parse_args()

print(f"""meta:
  configVersion: "0.3"
  strict_validation: false
systemtender:
  type: "bench_generic"
settings:
  generic:
    param_0:
      constraints:
        - {{step: 25.0, lower: 0.0, upper: 100.0}}
run:
  parallel: 1
interference_detection:
  # precision is NOT declared here: the estate's settings tree carries it
  # (policy/convergence_fraction, frozen at spawn). SILENT by design.
  group: {a.group}
  mode: active
  min_optimize_trials: 15
  hold_calib_trials: 5
  push_block_size: {a.push}
  pause_block_size: {a.pause}
  cooldown_trials: 5
  hold_params:
    param_0: 50.0
reconnaissance:
  type: http
  http:
    url: "{a.recon_url}"
objectives:
  - name: "objective_0"
    direction: maximize
    reconnaissance:
      service: http
      path: /metrics/json
      key: objective_0
      stabilization_seconds: 0
      samples: 3
      interval: 0
      aggregation: median
rollback_strategies:
  standard:
    consecutive_failures: 10
    target_state: "previous"
    max_attempts: 3
    on_failure: "continue"
    timeout_seconds: 60
    after:
      action: continue
effectuation:
  type: http
  targetRefs:
    - "{a.target_id}"
  endpoint_config:
    method: POST
    path: /apply
    timeout_seconds: 30
""")
