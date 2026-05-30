# Spec

## Suite Contract

- Suite path: full
- Work Item / FR locator: #1153 / #1145
- Story Readiness source: GitHub Work Item body is the scoped carrier.
- Story Business Confirmation source: governance regression only; business semantics are not required.
- Full suite artifacts not_applicable: none.

## Goal

Prove the end-to-end governance chain consumes suite automation across PR gate, merge-ready, closeout, issue, Project, target branch, and merge commit evidence.

## Scope

In scope:

- Non-mutating fixture inputs for issue, PR, Project, status checks, and target branch containment.
- PR gate and merge-ready consumption of suite evidence before merge.
- Closeout and reconciliation consumption of merged PR, issue state, Project status, target branch, merge commit, review, and merge-ready evidence.
- Negative proof that a merged PR alone is not enough to complete closeout.

Out of scope:

- Live GitHub mutation in fixtures.
- #1152 generated skills parity ownership.
- Parent #1145 or #1107 closeout.
- spec-kit `/speckit.*` commands or `.specify/` layout.

## Scenarios

### Scenario S1

Given a fixture Work Item has authored suite evidence, review allow evidence, merge-ready pass evidence, a merged PR payload, issue closed readback, Project Done readback, required checks success, and a target branch containing the merge commit
When closeout and reconciliation checks consume the fixture
Then the chain passes only because all host and Loom evidence are present together.

### Scenario S2

Given the same fixture has a merged PR payload but the issue remains open or Project is not Done
When closeout and reconciliation checks consume the fixture
Then the chain blocks and reports that PR merged alone is only a merge locator, not closeout completion.

### Scenario S3

Given PR gate and merge-ready consume the current PR head and authored full suite artifacts
When the fixture PR body is checked
Then the PR body must bind `Loom Work Item: WI-1153`, the branch, and the head SHA before host merge can be considered.

## Acceptance Criteria

- A1: `tools/check_cli_contract.py` asserts non-mutating closeout/reconciliation fixture payloads for pass and PR-merged-alone negative cases.
- A2: shared `loom_flow.py` exposes issue, PR, and Project payload fixture inputs for closeout/reconciliation checks without writing host state.
- A3: source/generated/runtime copies remain synchronized.
- A4: formal WI-1153 carriers record workspace entry, branch, PR/head placeholder, validation evidence, guardrails, and main-thread closeout ownership.
