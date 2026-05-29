# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: .loom/specs/WI-1151/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1151/spec.md
  - Acceptance ids / locators: A1-A4 in .loom/specs/WI-1151/spec.md
  - Story Readiness consumed state: #1151 issue body
  - Story Business Confirmation consumed state: skipped for governance-only regression behavior
- Produces:
  - Validation strategy by scenario: focused CLI contract fixture plus source and installed `loom_check` scaffold mutation boundary assertions.
  - Fresh verification evidence expectation: .loom/progress/WI-1151.md
- Locator:
  - Plan locator: .loom/specs/WI-1151/plan.md

## Implementation Goal

- Add a shared `loom_check` helper that exercises scaffold dry-run, scaffold apply, and forbidden host truth surfaces in temporary fixture targets.
- Call that helper from the existing source review-run fixture and installed pre-merge fixture.
- Synchronize generated/runtime copies without changing scaffold product behavior or adding artifact types.

## Phases

### Phase 1

- Objective: Add scaffold mutation boundary helper.
- Deliverable: shared helper in `src/skills/shared/scripts/loom_check.py`.
- Exit condition: py-compile and focused source-self fixture pass.

### Phase 2

- Objective: Wire source and installed fixture chains.
- Deliverable: source review-run and installed pre-merge paths call the helper.
- Exit condition: `tools/loom_check.py --profile source --source-surface source-self-fixture .` passes.

### Phase 3

- Objective: Keep generated/runtime surfaces synchronized.
- Deliverable: synced `skills/shared/scripts/loom_check.py`, `.loom/bin/loom_check.py`, and `examples/new-project/.loom/bin/loom_check.py`.
- Exit condition: `tools/skills_surface.py check` and contract-only source surface pass.

## Constraints

- No scaffold artifact types beyond contracted suite artifacts.
- No host, review, merge-ready, closeout, generated skill, Project, or GitHub truth mutation by scaffold commands.
- No `/speckit.*` command names or `.specify/` layout.
- Do not close #1151 or parent #1145/#1107 from this worker.

## Validation

- Scenario mapping:
  - S1 -> automated validation evidence: `require_scaffold_mutation_boundary_validation` dry-run snapshot assertion.
  - S2 -> automated validation evidence: `require_scaffold_mutation_boundary_validation` apply created-locator assertion.
  - S3 -> automated validation evidence: `require_scaffold_mutation_boundary_validation` forbidden truth snapshot assertion.
- Acceptance mapping:
  - A1 -> test evidence: `tools/check_cli_contract.py` scaffold dry-run/apply and forbidden truth fixtures.
  - A2 -> test evidence: source `loom_check` source-self fixture invocation.
  - A3 -> test evidence: installed pre-merge chain inside source-self fixture invocation.
  - A4 -> structural check: runtime copy parity and focused forbidden surface scan.
- Automated checks:
  - `git diff --check`
  - focused `rg`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py .loom/bin/loom_check.py examples/new-project/.loom/bin/loom_check.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Review And Closeout

- Review needed before merge-ready: implementation review by main thread / PR reviewer.
- Required coordination after merge: parent FR #1145 progress consumption by main thread only.
- Rollback boundary: revert WI-1151 fixture helper, runtime copies, and WI-1151 Loom carriers.
