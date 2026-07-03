# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1943 is a bounded gate-consumption bug fix over already observed PR #1942 evidence and does not introduce new product behavior, host writes, release mechanics, or security/permission semantics; consumer boundary: suite validate, review, PR gate, merge-ready, and closeout may consume this minimal suite; recheck condition: require full suite artifacts if scope expands into new gate schemas, host policy mutation, release mechanics, or broad closeout redesign.
- Consumes:
  - Spec locator: .loom/specs/WI-1943/spec.md
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1, A2
  - Story Readiness consumed state: not_applicable; bug fix from observed gate failure.
  - Story Business Confirmation consumed state: not_applicable; no business semantics change.
- Produces:
  - Validation strategy by scenario: targeted CLI contract fixtures.
  - Test strategy by acceptance: controlled-merge and governance-closeout surfaces.
  - Fresh verification evidence expectation: local command outputs recorded in progress/review.
- Locator:
  - Plan locator: .loom/specs/WI-1943/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1943/spec.md; #1943.
  - Freshness rule: stale if gate payload schema or closeout role semantics change.

## Implementation Goal

Patch the shared `loom_flow.py` consumers at the common gate points and add focused contract fixtures.

## Deferred Items

None.

## Phases

### Phase 1

- Objective: Update retained PR gate consumption for terminal closeout PRs.
- Deliverable: `retained_pr_gate_consumption` accepts passed terminal closeout consumption without relaxing ordinary implementation paths.
- Exit condition: controlled-merge fixture passes.

### Phase 2

- Objective: Update closeout backlink readback for final closeout PRs missing retained merge-ready attempts.
- Deliverable: closeout consumes implementation PR host checks as legacy merge-ready evidence.
- Exit condition: governance-closeout fixture and real PR #1942 closeout replay pass.

## Constraints

- Keep implementation PR merge checkpoint requirements unchanged.
- Do not mutate GitHub rulesets or branch protection.
- Keep runtime copies and plugin payload hash synchronized.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py examples/new-project/.loom/bin/loom_flow.py tools/check_cli_contract.py`
  - `git diff --check`
  - `python3 tools/check_cli_contract.py --surface controlled-merge --surface governance-closeout`
  - `python3 tools/check_npm_package.py --surface aggregate`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`
- Runtime evidence:
  - Real PR #1942 `merge check` replay passed with retained terminal closeout PR gate.
  - Real PR #1942 post-merge `closeout` replay passed.
  - `python3 tools/loom_check.py --profile source --source-surface contract-only .` remains blocked by unrelated demo consumer profile checks.
- Fresh verification evidence: .loom/progress/WI-1943.md

Scenario validation mapping:

- S1 -> automated test evidence: `python3 tools/check_cli_contract.py --surface controlled-merge`.
- S2 -> automated test evidence: `python3 tools/check_cli_contract.py --surface governance-closeout`.

Acceptance test mapping:

- A1 -> test evidence: controlled-merge fixture in `tools/check_cli_contract.py`.
- A2 -> test evidence: governance-closeout fixture in `tools/check_cli_contract.py`.
