# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: .loom/specs/WI-1715/spec.md
  - Implementation contract locator: .loom/specs/WI-1715/implementation-contract.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: not required
  - Story Business Confirmation consumed state: not required
- Produces:
  - Validation strategy by scenario: targeted CLI contract checks and direct JSON assertions.
  - Test strategy by acceptance: extend existing `adoption-host-metadata` surface.
  - Fresh verification evidence expectation: local validation summary before PR and PR head readback before merge-ready.
- Locator:
  - Plan locator: .loom/specs/WI-1715/plan.md
- Provenance:
  - Source spec / issue locator: .loom/specs/WI-1715/spec.md; issue #1715
  - Freshness rule: Re-run validation after any change to `tools/loom.py` or `tools/check_cli_contract.py`.

## Implementation Goal

Add one shared freshness diagnostic and wire it into the existing CLI outputs.

## Deferred Items

- None.

## Not Required Items

- Release execution: not required for WI-1715; owned by #1718.
- Plugin refresh apply UX: not required for WI-1715; owned by #1716.

## Phases

### Phase 1

- Objective: Add shared freshness reporting.
- Deliverable: `version_freshness()` and `cli-plugin-freshness` action.
- Exit condition: `version`, `doctor`, `host doctor`, and `upgrade-plan` expose the freshness block.

### Phase 2

- Objective: Cover the output contract.
- Deliverable: focused adoption host metadata contract checks.
- Exit condition: target surface and diff checks pass.

## Constraints

- Keep root CLI, plugin surface version, contract version, and plugin payload version as separate version lines.
- Do not mutate Codex plugin state from diagnostic commands.
- Do not restore single SKILL installation.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - `git diff --check`
- Manual checks:
  - `LOOM_TEST_NPM_LATEST_VERSION=99.0.0 python3 tools/loom.py version --json`
  - `LOOM_TEST_NPM_LATEST_VERSION=__unreadable__ python3 tools/loom.py version --json`
  - `LOOM_SKIP_NPM_LATEST=1 python3 tools/loom.py upgrade-plan --target . --host codex --json`
- Runtime evidence: local command output summarized in .loom/progress/WI-1715.md.
- Behavior evidence: .loom/specs/WI-1715/evidence-map.md.
- Scenario validation mapping:
  - S1 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> automated validation: `LOOM_TEST_NPM_LATEST_VERSION=99.0.0 python3 tools/loom.py version --json`
  - S3 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`

## Test Strategy

- Regression coverage: extend the existing adoption host metadata surface.
- Cases intentionally not automated: real npm outage timing; simulated through `LOOM_TEST_NPM_LATEST_VERSION=__unreadable__`.
- Acceptance validation mapping:
  - A1 -> test evidence: `assert_version_freshness_contract`
  - A2 -> test evidence: `assert_version_freshness_contract`
  - A3 -> test evidence: `assert_version_freshness_contract`
  - A4 -> test evidence: `assert_version_freshness_contract`
  - A5 -> test evidence: `loom version` default output check

## Subagent Output Integration

- Owned outputs: none; no subagent output is integrated in this Work Item.
- Integration owner: main agent.
- Handoff notes locator: none.

## Dependencies

- Blocking inputs: #1713, #1714, #1719, #1720, and #1721 terminal evidence already merged before this lane.
- Required coordination: #1716 consumes this freshness action for refresh guidance.
- Rollback boundary: revert WI-1715 PR only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is not required for this issue-scoped CLI diagnostic change
- [x] Story business semantics are not required for this issue-scoped CLI diagnostic change
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
