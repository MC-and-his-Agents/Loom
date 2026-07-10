# WI-1534 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1534 is a bounded docs/skills/fixture convergence slice that documents already-implemented closeout freeze, closeout-specific gate, closeout queue/status, and closeout run surfaces. It does not add runtime behavior, host mutation, release execution, or new schema authority. consumer boundary: suite validate, docs/skills review, PR metadata, hosted checks, and #1515 final closeout may consume this minimal suite for closeout mode protocol alignment only. recheck condition: require full suite artifacts if scope expands into runtime behavior, hosted gate behavior, release/no-release final judgment, issue/PR mutation logic, security behavior, migration behavior, or new closeout schema. scope proof: `git diff origin/main...HEAD` must stay limited to WI-1534 carriers, closeout docs, closeout-related skill protocols/references, and targeted fixture/documentation checks. review requirement: current-head review must consume final docs/skills/fixture diff plus #1533/#1555/#1543/#1541 readback.

## Objective

Align closeout mode documentation, skill protocols, and regression fixtures so operators can choose inline, auto no-op, light, batched, or full closeout paths while consuming the stable `loom-closeout-specific-gate/v1` verdict contract.

## Acceptance Scenarios

### S1: Closeout modes are documented consistently

Given the closeout docs and skills are read, when an operator chooses a closeout path, then inline, auto no-op, light, batched, and full modes have consistent boundaries and escalation triggers.

### S2: Closeout-specific gate is linked to review escalation

Given a closeout-only PR or closeout freeze payload, when `closeout_specific_gate` blocks, then docs and skills direct the operator to resolve blockers or run full review / guardian instead of treating closeout as implementation approval.

### S3: Queue/status classification stays separate from canonical mode

Given closeout queue/status uses operational classifications, when docs mention queue status, then `auto_no_op`, `light_carrier_sync`, `batched_closeout`, `full_closeout`, and `blocked` are mapped to canonical modes without replacing them.

### S4: Fixtures guard the protocol

Given the docs/skills protocol is stable, when targeted CLI contract checks run, then closeout mode vocabulary, closeout-specific gate field names, and non-goal boundaries remain covered by fixture or documentation assertions.

## Non-Goals

- Do not implement runtime behavior beyond fixture/documentation assertions.
- Do not perform release, tag, npm publish, Project mutation, issue closure, PR merge, or batch closeout execution.
- Do not redefine #1513 failure classifier authority or #1515 release/no-release final closeout.
