# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator: .loom/specs/WI-1292/spec.md
- Consumes:
  - Spec locator: .loom/specs/WI-1292/spec.md
  - Scenario ids / locators: S1, S2, S3, S4
  - Acceptance ids / locators: A1, A2, A3, A4, A5
  - Completed dependency: #1452 closeout via PR #1614 and carrier-sync PR #1637
- Produces:
  - Validation strategy by scenario: targeted CLI contract fixture surface
  - Test strategy by acceptance: `controlled-merge` surface
  - Fresh verification evidence expectation: current PR head and hosted checks
- Locator:
  - Plan locator: .loom/specs/WI-1292/plan.md

- full-path-artifacts not_applicable rationale: WI-1292 uses the minimal suite because implementation is a bounded fixture addition in `tools/check_cli_contract.py`; consumer boundary: plan validation, review, merge-ready, and closeout consume this plan plus targeted verification evidence; recheck condition: expand to full suite if the work changes runtime behavior, adapter schemas, release publication, or live host settings.

## Implementation Goal

- Add a focused cross-repo review gate fixture helper.
- Keep runtime core unchanged and reuse existing pr-gate / controlled-merge fixture APIs.

## Phases

### Phase 1

- Objective: Add HotCP-style regression cases.
- Deliverable: post-merge review bypass, CI-only bypass, and stale/head drift assertions.
- Exit condition: targeted `controlled-merge` surface passes.

### Phase 2

- Objective: Add WebEnvoy/Syvert-style regression cases.
- Deliverable: guardian failed/pending block, advisory non-substitution, and conflicting/pending triggered verdict assertions.
- Exit condition: targeted `controlled-merge` surface passes.

### Phase 3

- Objective: Sync governance carriers and hosted gate inputs.
- Deliverable: WI-1292 carriers, review records, PR metadata readback, hosted checks.
- Exit condition: controlled merge passes and #1292 closes.

## Scenario Mapping

- S1 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge` HotCP post-merge review bypass and CI-only bypass assertions.
- S2 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge` HotCP stale/head drift assertion.
- S3 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge` WebEnvoy failed/pending guardian triggered-check assertions.
- S4 -> automated validation evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge` Syvert advisory, failed verdict conflict, and pending verdict assertions.

## Acceptance Mapping

- A1 -> test evidence: HotCP post-merge review bypass fixture assertion in `tools/check_cli_contract.py`.
- A2 -> test evidence: HotCP CI-only bypass fixture assertion in `tools/check_cli_contract.py`.
- A3 -> test evidence: HotCP stale/head drift fixture assertion in `tools/check_cli_contract.py`.
- A4 -> behavior evidence: WebEnvoy failed/pending triggered-check assertions plus inventory entries in `docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json`.
- A5 -> behavior evidence: Syvert advisory, failed, and pending triggered-check assertions plus inventory entries in `docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json`.

## Constraints

- Do not change runtime product logic for #1292.
- Do not mutate live GitHub settings.
- Do not include #1293 release work or #1285 final closeout.
- Keep subagent output advisory until integrated and validated by the main lane.

## Validation

- Automated checks:
  - `python3 -m py_compile tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`
  - `python3 -m json.tool docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json >/dev/null`
  - `git diff --check`
- Hosted checks:
  - PR metadata readback
  - `loom-pr-merge-gate`
  - `loom-check`
  - package/install checks required by the repository
- Manual checks:
  - Confirm #1452 is closed and #1292 consumes rather than reimplements triggered-check behavior.

## Test Strategy

- Regression cases are expressed as in-repo CLI contract fixtures.
- Downstream migration inventory records the WebEnvoy/Syvert failed and pending triggered-check consumption cases.
- The helper uses existing fixture builders and existing pr-gate / controlled-merge commands.
- The controlled-merge triggered check cases prove required checks can stay green while non-required guardian/integration checks still block.
