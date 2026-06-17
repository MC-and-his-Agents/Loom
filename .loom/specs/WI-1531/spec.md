# WI-1531 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1531 is a bounded docs-only governance contract slice that defines the `loom-closeout-freeze/v1` terminal profile and a non-executable fixture inventory. A formal spec/plan/implementation-contract suite would restate the same contract without adding a separate product/runtime implementation contract. consumer boundary: this decision only skips formal suite artifacts; fact-chain/status carriers, current-head review, PR metadata/readback, hosted checks, PR gate, no_release judgment, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if scope expands into CLI/runtime behavior, hosted workflow behavior, closeout-specific gate behavior, final #1510/#1513 field naming, executable fixtures, release mechanics, security/privacy behavior, migration behavior, or external visible actions. scope proof: `git diff origin/main...HEAD` must stay limited to WI-1531 carriers, `docs/methodology/harness/gate-freeze.md`, `docs/methodology/harness/closeout-gate.md`, and `docs/evidence/fixtures/closeout-freeze-terminal-profile-fixtures.json`. review requirement: current-head review must consume the final docs/fixture diff, pending field inventory, dependency boundary for #1532/#1533/#1534, and proof that no runtime, hosted gate, release, or implementation behavior changed.

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
