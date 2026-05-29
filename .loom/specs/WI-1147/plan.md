# Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifact skip is consumed from .loom/specs/WI-1147/spec.md.
- Consumes:
  - Spec locator: .loom/specs/WI-1147/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1147/spec.md
  - Acceptance ids / locators: A1-A4 in .loom/specs/WI-1147/spec.md
  - Story Readiness consumed state: #1147 issue body
  - Story Business Confirmation consumed state: skipped for governance-only regression behavior
- Produces:
  - Validation strategy by scenario: CLI contract fixture plus source-self and installed `loom_check` fixture assertions.
  - Test strategy by acceptance: focused contract/source checks and generated runtime parity checks.
  - Fresh verification evidence expectation: .loom/progress/WI-1147.md
- Locator:
  - Plan locator: .loom/specs/WI-1147/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1147/spec.md, #1147
  - Freshness rule: update validation summary after final local checks.

## Implementation Goal

- Make the minimal suite happy path an explicit E2E governance regression rather than an incidental temporary fixture.
- Prove both source-local and installed-runtime fixture paths consume the valid minimal suite before downstream review/merge-ready style gates.

## Future Items

### Future Item 1

- Locator: #1148 full suite happy path fixture
- Reason: #1147 only proves the minimal path.
- Activation condition: after #1147 closes.
- Does not currently block: #1147 minimal path fixture.
- Statement: this future item is not completed by #1147.

### Future Item 2

- Locator: #1149 / #1150 / #1151 / #1152 / #1153
- Reason: fail-closed, scaffold, generated-skill parity, and PR gate/merge-ready/closeout integration fixtures are separate Work Items.
- Activation condition: after their owning Work Items start.
- Does not currently block: #1147 minimal path fixture.
- Statement: these future items are not completed by #1147.

## Phases

### Phase 1

- Objective: Extend CLI contract minimal fixture to include evidence and carrier happy path.
- Deliverable: `tools/check_cli_contract.py` writes a complete minimal fixture and asserts suite/evidence/carrier validation pass.
- Exit condition: `python3 tools/check_cli_contract.py` passes.

### Phase 2

- Objective: Add source and installed `loom_check` fixture assertions.
- Deliverable: shared `loom_check` helper verifies suite/evidence/carrier pass for source review-run and installed pre-merge fixtures.
- Exit condition: `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .` passes or reaches only unrelated pre-existing failures with clear evidence.

### Phase 3

- Objective: Keep runtime surfaces synchronized.
- Deliverable: copy shared runtime update to `src/skills`, `.loom/bin`, and demo installed runtime.
- Exit condition: focused `cmp`/`rg`, `skills_surface`, and contract-only checks pass.

## Constraints

- Architectural or governance constraints: fixture output is evidence only and cannot replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- Workspace / rollout constraints: issue-scoped branch/worktree/PR only.
- Purity or scope constraints: no full path fixture, no negative fixture, no host writes beyond normal issue/PR/Project closeout, no `/speckit.*`, no `.specify/`.

## Validation

- Scenario mapping:
  - S1 -> automated validation evidence: suite validate pass payload.
  - S2 -> automated validation evidence: suite evidence validate pass payload.
  - S3 -> automated validation evidence: suite carrier validate pass payload.
- Acceptance mapping:
  - A1 -> test evidence: tools/check_cli_contract.py minimal happy path fixture.
  - A2 -> test evidence: source-self loom_check helper invocation.
  - A3 -> test evidence: installed pre-merge loom_check helper invocation.
  - A4 -> structural check: runtime copy parity and focused forbidden surface scan.
- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_cli_contract.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py .loom/bin/loom_check.py examples/new-project/.loom/bin/loom_check.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
  - `git diff --check`
  - focused `rg` for minimal happy path and forbidden external command/layout strings
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks: inspect generated/source runtime copies for synchronization.
- Runtime evidence: .loom/progress/WI-1147.md
- Behavior evidence: tools/check_cli_contract.py; skills/shared/scripts/loom_check.py
- Fresh verification evidence: .loom/progress/WI-1147.md

## Review And Closeout

- Review or reconciliation needed before merge-ready: spec review, implementation review, PR gate, merge-ready, controlled merge, closeout.
- Required coordination: parent FR #1145 and phase #1107 progress comments after closeout.
- Rollback boundary: revert #1147 fixture assertions and WI-1147 Loom carriers only.
