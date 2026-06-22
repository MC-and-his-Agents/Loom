# WI-1720 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1720`
- Consumes:
  - Spec locator: `.loom/specs/WI-1720/spec.md`
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A4
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: targeted CLI contract fixtures plus doc-sync assertions.
  - Test strategy by acceptance: `adoption-host-metadata` and aggregate CLI contract checks.
  - Fresh verification evidence expectation: `.loom/progress/WI-1720.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1720/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1720 and `.loom/specs/WI-1720/spec.md`
  - Freshness rule: Re-run validation after CLI, docs, checker, or carrier changes.

## Implementation Goal

- Add a stable `host-plugin-refresh-boundary` guidance action for Codex target install/upgrade surfaces.
- Reword target install/upgrade summaries and fail-closed reasons so they describe repository installed-state/adoption metadata only.
- Guard README/source skill wording and CLI payload shape in `tools/check_cli_contract.py`.

## Excluded Items

- Payload hash generation, comparison, or freshness reports.
- Host plugin source/cache readback semantics beyond pointing to existing host commands.
- Release/version/npm/publish files and `packages/loom-installer/**`.
- PR creation, guardian, or high-cost hosted checks.

## Phases

### Phase 1

- Objective: Update CLI payloads.
- Deliverable: `tools/loom.py` emits host refresh guidance and target-only wording.
- Exit condition: py_compile passes and targeted fixture can inspect payloads.

### Phase 2

- Objective: Add targeted contract coverage.
- Deliverable: `tools/check_cli_contract.py` checks install, upgrade-plan, upgrade, and docs snippets.
- Exit condition: `tools/check_cli_contract.py --surface adoption-host-metadata` passes.

### Phase 3

- Objective: Sync minimal docs and Loom carriers.
- Deliverable: README, README.zh-CN, `src/skills/README.md`, and WI-1720 carriers.
- Exit condition: suite validate/evidence/carrier validate and build gate pass.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface reference-integrity`
  - `git diff --check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1720 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1720 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1720 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1720 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1720 --build-evidence .loom/progress/WI-1720-build-evidence.json`
- Manual checks: inspect `git diff --stat` and confirm no forbidden paths were touched.
- Runtime evidence: `.loom/progress/WI-1720.md`
- Behavior evidence: `tools/loom.py`, docs snippets, and CLI contract fixtures.
- Scenario validation mapping:
  - S1 -> automated evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`.
  - S2 -> automated evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`.
  - S3 -> automated evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`.
- Fresh verification evidence: `.loom/progress/WI-1720.md`
- Execution ledger plan locator: `.loom/specs/WI-1720/plan.md`
- Execution ledger validation evidence locator: `.loom/progress/WI-1720.md`

## Test Strategy

- TDD or test-first expectation: add/refresh assertions before final validation.
- Regression coverage to add or preserve: `adoption-host-metadata` now covers target install/upgrade versus Codex host provider boundary.
- Cases intentionally not automated: full prose quality beyond required snippets.
- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - A4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface adoption-host-metadata`
