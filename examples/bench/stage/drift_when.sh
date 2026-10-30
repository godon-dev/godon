#!/usr/bin/env bash
# drift_when.sh — the stage hand for the bench drift door (v1).
#
# Fires POST /{node}/drift/start when a BENCH-OBSERVABLE condition
# holds. The bench speaks for itself: its uptime, its tick counter.
# Story cues that live in the ENGINE (hold landed, wish state) are
# fired by the officer through the same door — the engine is the
# subject and must not cue its own world.
#
# The walk-finished tell is bench-local: the node's metrics tick FROZEN
# across two reads at least --window seconds apart, with the bench
# answering both reads. (The full estate tell adds the tender
# heartbeat; that check lives with the officer, not the world.)
#
# Usage:
#   drift_when.sh --bench http://127.0.0.1:8090 --node node-1 \
#     (--at-minute N | --when walk-finished) \
#     --rate 0.001 [--cap 0.15] [--name cue] \
#     [--window 90] [--poll 15] [--deadline 3600]
#
# Exit 0 = the drift was cued (prints the door's receipt).
# Exit 2 = condition never held before --deadline.
set -euo pipefail

BENCH=""; NODE=""; MODE=""; AT_MIN=""; RATE=""; CAP=""; NAME="stage"
WINDOW=90; POLL=15; DEADLINE=3600
while [ $# -gt 0 ]; do
  case "$1" in
    --bench) BENCH="$2"; shift 2 ;;
    --node) NODE="$2"; shift 2 ;;
    --at-minute) MODE=minute; AT_MIN="$2"; shift 2 ;;
    --when) MODE="$2"; shift 2 ;;
    --rate) RATE="$2"; shift 2 ;;
    --cap) CAP="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --window) WINDOW="$2"; shift 2 ;;
    --poll) POLL="$2"; shift 2 ;;
    --deadline) DEADLINE="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
[ -n "$BENCH" ] && [ -n "$NODE" ] && [ -n "$RATE" ] || { echo "--bench, --node and --rate are required" >&2; exit 1; }
[ "$MODE" = "minute" ] || [ "$MODE" = "walk-finished" ] || { echo "need --at-minute N or --when walk-finished" >&2; exit 1; }

BODY() {
  if [ -n "$CAP" ]; then
    printf '{"rate_per_second": %s, "cap": %s, "name": "%s"}' "$RATE" "$CAP" "$NAME"
  else
    printf '{"rate_per_second": %s, "name": "%s"}' "$RATE" "$NAME"
  fi
}

fire() {
  local R CODE
  R=$(curl -s -m 10 -w "\n%{http_code}" -X POST "$BENCH/$NODE/drift/start" \
    -H "Content-Type: application/json" -d "$(BODY)") || { echo "door unreachable" >&2; return 1; }
  CODE=$(echo "$R" | tail -1)
  if [ "$CODE" = "200" ]; then
    echo "CUED $(date -u +%FT%TZ) $(echo "$R" | head -n -1)"
    return 0
  elif [ "$CODE" = "409" ]; then
    echo "ALREADY-RUNNING $(date -u +%FT%TZ) $(echo "$R" | head -n -1)"
    return 0
  fi
  echo "door refused http=$CODE: $(echo "$R" | head -n -1)" >&2
  return 1
}

START=$(date +%s)
if [ "$MODE" = "minute" ]; then
  echo "waiting for bench uptime >= ${AT_MIN}m (poll ${POLL}s)…" >&2
  while :; do
    U=$(curl -s -m 10 "$BENCH/$NODE/drift/state" | python3 -c 'import json,sys; print(json.load(sys.stdin)["uptime_secs"])' 2>/dev/null) || U=0
    if python3 -c "import sys; sys.exit(0 if float('$U') >= float('$AT_MIN')*60 else 1)" 2>/dev/null; then
      fire; exit $?
    fi
    [ $(( $(date +%s) - START )) -ge "$DEADLINE" ] && { echo "deadline hit before minute ${AT_MIN}" >&2; exit 2; }
    sleep "$POLL"
  done
fi

# walk-finished: tick frozen across two reads >= WINDOW seconds apart
echo "watching $NODE for a frozen tick (window ${WINDOW}s, poll ${POLL}s)…" >&2
LAST_TS=0; LAST_TICK=""
while :; do
  TS=$(date +%s)
  TICK=$(curl -s -m 10 "$BENCH/$NODE/metrics/json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tick"))' 2>/dev/null) || TICK=""
  if [ -n "$TICK" ] && [ "$TICK" != "None" ]; then
    if [ $LAST_TS -gt 0 ] && [ $(( TS - LAST_TS )) -ge "$WINDOW" ] && [ "$TICK" = "$LAST_TICK" ]; then
      echo "FINISH-TELL tick=$TICK frozen across ${WINDOW}s+" >&2
      fire; exit $?
    fi
    if [ "$TICK" != "$LAST_TICK" ]; then LAST_TS=$TS; LAST_TICK=$TICK; fi
  fi
  [ $(( $(date +%s) - START )) -ge "$DEADLINE" ] && { echo "deadline hit before a frozen tick" >&2; exit 2; }
  sleep "$POLL"
done
