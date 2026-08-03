# Open Issue: Coordination Table Lifecycle

## Problem

Single global coordination table (sender_lease, interference_active_breeders,
detection_readiness) in YugabyteDB shared across ALL breeders. When breeders
are purged between sweep cells, these tables retain stale state. Next cell's
breeders see stale leases and get stuck in HOLD.

Current workaround: full reinstall per cell.

## Why "all breeders gone" is a bad cleanup signal

In production, breeders are always running. The global table can never know
when a logical "session" or "group" has ended. Purging based on zero active
breeders is unrealistic.

## Proposed direction

Group breeders by a tag (e.g. `detection_group: sweep-cell-01`). Scope
coordination tables per group. When a group's breeders are purged, clean
up only that group's coord state. Multiple groups can coexist without
interference.

This needs engine work in detection_coordinator.py — the lease table
queries would need a `WHERE group_tag = ?` filter.
