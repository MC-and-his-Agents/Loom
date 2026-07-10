# WI-1513 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1513 is a bounded gate freeze classifier contract slice with deterministic runtime and CLI contract coverage; consumer boundary: suite validate, freeze snapshot consumers, hosted admission #1512, closeout gate #1533, docs/skills #1514/#1534, review, merge-ready, PR/CI, target branch validation, and milestone closeout may consume this minimal suite only for classifier vocabulary and next-action mapping; recheck condition: require broader suite artifacts if scope expands into hosted admission behavior, closeout gate behavior, PR metadata rendering, release behavior, closeout run mutation, security/privacy behavior, or external host writes.

## Objective

Make `loom-gate-freeze/v1` expose a normalized `loom-failure-classifier/v1` payload so downstream gates can consume stable categories and next actions instead of raw local failure-kind strings.

## Acceptance Scenarios

### S1: Gate freeze failures are classified

Given a gate freeze blocked input such as PR metadata drift, carrier refresh needed, shadow stale, or review stale, the JSON payload includes a normalized classifier and concrete next action.

### S2: Downstream classifier vocabulary is stable

Given hosted admission and closeout consumers need common names, the supported classifier list includes the #1513 categories for host API unreadable, permission, hosted snapshot mismatch, suite evidence contract invalid, task carrier contract invalid, unsupported command surface, and release evidence phase error.

## Acceptance Criteria

- A1: Gate freeze failure classifier uses schema `loom-failure-classifier/v1`.
- A2: Supported classifier vocabulary includes the #1513 categories needed by #1512/#1533/#1534.
- A3: PR metadata drift is classified separately from code semantics.
- A4: Carrier, shadow, review, suite evidence, task carrier, host API, permission, snapshot mismatch, command surface, and release phase classes have next_action guidance.
- A5: Existing gate pass/block/fallback behavior is unchanged.

## Non-Goals

- Do not implement hosted gate admission consumption in #1512.
- Do not implement closeout-specific gate behavior in #1533.
- Do not implement PR metadata render/update/readback in #1541.
- Do not implement Work Item startup audit #1542, one-shot post-merge closeout #1555, or release/no-release closeout #1515.
