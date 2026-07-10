# WI-1510 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1510 is a bounded gate freeze input contract slice with deterministic runtime and CLI contract coverage; consumer boundary: suite validate, freeze snapshot consumers, hosted admission #1512, review, merge-ready, PR/CI, target branch validation, and milestone closeout may consume this minimal suite only for generic carrier refresh and shadow freshness inputs; recheck condition: require broader suite artifacts if scope expands into hosted admission behavior, closeout terminal profile semantics, PR metadata rendering, release behavior, closeout item binding, security/privacy behavior, or external host writes.

## Objective

Make `loom-gate-freeze/v1` expose carrier refresh dry-run state and shadow source-hash freshness as explicit machine-readable input bindings before hosted gate admission consumes the snapshot.

## Acceptance Scenarios

### S1: Carrier refresh is frozen

Given a gate freeze snapshot is generated, it includes `input_bindings.carrier_refresh` with schema `loom-gate-freeze-carrier-refresh/v1`, the dry-run payload, pending refresh actions, and typed blocking output when carrier refresh is stale.

### S2: Shadow freshness is frozen

Given declared shadow evidence has source hashes, the snapshot includes `input_bindings.shadow_freshness` with per-shadow records containing path, surface, freshness, drift kind, refreshability, next action, and current/expected source hashes.

### S3: Refresh suggestions are executable

Given freeze input drift is refreshable, `readiness.refresh_suggestions` only references existing supported commands or existing runtime paths and does not suggest the unsupported `loom shadow-parity` wrapper command.

## Non-Goals

- Do not implement hosted gate admission consumption in #1512.
- Do not implement closeout terminal profile behavior, closeout-specific gate, release/no-release closeout, or milestone/12 final closeout.
- Do not implement PR metadata render/update/readback, closeout `--item` binding, one-shot post-merge closeout run, or broad failure classifier taxonomy beyond fields needed by this slice.
