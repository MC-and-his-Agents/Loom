# Plan

## Suite Contract

- Suite path consumed: full
- Consumes:
  - Spec locator: .loom/specs/WI-1148/spec.md
  - Suite index locator: .loom/specs/WI-1148/suite-index.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1148/spec.md
  - Acceptance ids / locators: A1-A4 in .loom/specs/WI-1148/spec.md
  - Story Readiness consumed state: #1148 issue body
  - Story Business Confirmation consumed state: skipped for governance-only regression behavior
- Produces:
  - Validation strategy by scenario: CLI contract fixture plus source-self and installed `loom_check` fixture assertions.
  - Test strategy by acceptance: focused contract/source checks and generated runtime parity checks.
  - Fresh verification evidence expectation: .loom/progress/WI-1148.md
- Locator:
  - Plan locator: .loom/specs/WI-1148/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1148/spec.md, #1148
  - Freshness rule: update validation summary after final local checks.

## Implementation Goal

- Make the full suite happy path an explicit E2E governance regression rather than a shallow inspect-only fixture.
- Prove both source-local and installed-runtime fixture paths consume full suite required, conditional, evidence, consistency, and carrier artifacts.

## Future Items

### Future Item 1

- Locator: #1149 / #1150
- Reason: fail-closed missing artifact, invalid skip-rationale, stale evidence, and host conflict fixtures are separate negative Work Items.
- Activation condition: after their owning Work Items start.
- Does not currently block: #1148 full happy path fixture.
- Statement: these future items are not completed by #1148.

### Future Item 2

- Locator: #1151 / #1152 / #1153
- Reason: scaffold, generated-skill parity, and PR gate/merge-ready/closeout integration fixtures are separate Work Items.
- Activation condition: after their owning Work Items start.
- Does not currently block: #1148 full happy path fixture.
- Statement: these future items are not completed by #1148.

## Phases

### Phase 1

- Objective: Extend CLI contract full fixture to include evidence and carrier happy path.
- Deliverable: `tools/check_cli_contract.py` writes a complete full fixture and asserts suite/evidence/carrier validation pass.
- Exit condition: `python3 tools/check_cli_contract.py` passes.

### Phase 2

- Objective: Add source and installed `loom_check` full fixture assertions.
- Deliverable: shared `loom_check` helper verifies suite/evidence/carrier pass for source review-run and installed pre-merge fixtures.
- Exit condition: `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .` passes.

### Phase 3

- Objective: Keep runtime surfaces synchronized.
- Deliverable: copy shared runtime update to `src/skills`, `.loom/bin`, generated skills, and demo installed runtime.
- Exit condition: focused `rg`, `skills_surface`, and contract-only checks pass.

## Constraints

- Architectural or governance constraints: fixture output is evidence only and cannot replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- Workspace / rollout constraints: issue-scoped branch/worktree/PR only.
- Purity or scope constraints: no negative fixture, no scaffold fixture, no host writes beyond normal issue/PR/Project closeout, no `/speckit.*`, no `.specify/`.

## Validation

- Scenario mapping:
  - S1 -> automated validation evidence: suite validate pass payload.
  - S2 -> automated validation evidence: suite evidence validate pass payload.
  - S3 -> automated validation evidence: suite carrier validate pass payload.
- Acceptance mapping:
  - A1 -> test evidence: tools/check_cli_contract.py full happy path fixture.
  - A2 -> test evidence: source-self loom_check helper invocation.
  - A3 -> test evidence: installed pre-merge loom_check helper invocation.
  - A4 -> structural check: runtime copy parity and focused forbidden surface scan.
- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_cli_contract.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py .loom/bin/loom_check.py examples/new-project/.loom/bin/loom_check.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
  - `git diff --check`
  - focused `rg` for full happy path and forbidden external command/layout strings
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks: inspect generated/source runtime copies for synchronization.
- Runtime evidence: .loom/progress/WI-1148.md
- Behavior evidence: tools/check_cli_contract.py; skills/shared/scripts/loom_check.py
- Fresh verification evidence: .loom/progress/WI-1148.md

## Review And Closeout

- Review or reconciliation needed before merge-ready: spec review, implementation review, PR gate, merge-ready, controlled merge, closeout.
- Required coordination: parent FR #1145 and phase #1107 progress comments after closeout.
- Rollback boundary: revert #1148 fixture assertions and WI-1148 Loom carriers only.
