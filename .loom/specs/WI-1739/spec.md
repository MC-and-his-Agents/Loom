# WI-1739 Spec

## Problem

Before WI-1739, `loom ship --apply` could repair PR metadata before merge gates, but carrier refresh and shadow parity still required operators to remember separate commands. This left the main ship path vulnerable to stale carrier or shadow evidence being discovered late by PR gate or hosted checks.

## Acceptance Criteria

- AC-1: `loom ship --apply` runs safe metadata repair before PR metadata preflight.
- AC-2: `loom ship --apply` runs carrier refresh with `--apply` before PR metadata preflight, PR gate, and controlled merge check.
- AC-3: `loom ship --apply` runs blocking all-surface shadow parity after carrier refresh and before PR metadata preflight, PR gate, and controlled merge check.
- AC-4: If carrier refresh or shadow parity blocks, `loom ship --apply` stops before merge and returns short diagnostics with a single next action.
- AC-5: Dry-run `loom ship` remains non-mutating.
- AC-6: Implementation drift and stale review semantics are still handled by PR gate; this work does not bypass current-head review requirements.

## Non-Goals

- No release publish behavior.
- No #1742 inline/host-only closeout e2e expansion.
- No broad rewrite of metadata repair internals.
