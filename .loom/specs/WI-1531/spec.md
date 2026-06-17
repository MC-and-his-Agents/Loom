# WI-1531 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1531 is a bounded docs-only contract freeze for the closeout terminal profile. It does not change runtime behavior, hosted workflows, host writes, release mechanics, security permissions, or persistence outside versioned documentation and fixture inventory. consumer boundary: #1532/#1533/#1534 may consume this contract, pending field inventory, and fixture inventory; PR gate, review, and closeout must still consume normal repo-local and host readback. recheck condition: require a full suite if #1531 expands into CLI behavior, hosted workflow behavior, release semantics, security/privacy behavior, migration behavior, or external visible actions.

## Objective

Define `loom-closeout-freeze/v1` as the terminal closeout profile of the gate freeze contract so closeout-only PRs can carry terminal facts without becoming a second truth source or hiding drift.

## Acceptance Scenarios

### S1: Terminal profile boundary is explicit

Given the contract is read, it states that `loom-closeout-freeze/v1` is docs/fixture contract only in #1531 and does not implement runtime behavior or replace closeout, PR gate, review, release/no-release, or host/git readback.

### S2: Terminal subject and facts are defined

Given a future closeout freeze consumer is implemented, it can identify required subject fields, terminal facts, carrier bindings, retained review, release boundary, allowed paths, and pending upstream fields from the contract.

### S3: Closeout-only drift fails closed

Given a closeout-only PR includes implementation drift, release dispute, mixed batch risk, stale shadow, carrier drift, or host/git mismatch, the contract identifies a blocking closeout profile failure kind and next action.

### S4: Dependency lanes remain separated

Given #1532/#1533/#1534 are planned, the contract documents which fields are pending on #1510/#1512/#1513 and prevents those downstream work items from guessing schema names before upstream surfaces stabilize.

## Non-Goals

- No CLI implementation for `gate freeze --profile closeout`.
- No hosted admission workflow changes.
- No closeout-specific gate behavior changes.
- No final #1510 carrier/shadow field naming.
- No final #1513 classifier naming.
- No release/tag/npm/GitHub Release changes.
