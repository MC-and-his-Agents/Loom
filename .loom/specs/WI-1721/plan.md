# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1721/spec.md`
  - Implementation contract locator: `.loom/specs/WI-1721/implementation-contract.md`
  - Scenario ids / locators: S1-S3 in spec
  - Acceptance ids / locators: A1-A4 in spec
  - Story Readiness consumed state: not required
  - Story Business Confirmation consumed state: not required
- Produces:
  - Validation strategy by scenario: targeted CLI contract and live host doctor readback
  - Test strategy by acceptance: one existing contract surface extended
  - Fresh verification evidence expectation: latest validation summary in `.loom/progress/WI-1721.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1721/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1721 and `.loom/specs/WI-1721/spec.md`
  - Freshness rule: rerun after every code/test change in this Work Item.

## Implementation Goal

Deliver the smallest read-only `plugin_payload_readback` contract inside existing host doctor output.

Explicitly deferred: aggregate `version/doctor/upgrade-plan` freshness UX (#1715/#1716), broad fixtures (#1717), and v0.19.0 release (#1718).

## Phases

### Phase 1

- Objective: Add read-only layer metadata comparison.
- Deliverable: `tools/loom.py` reports `source-payload`, `marketplace-source`, and `runtime-cache`.
- Exit condition: live `host doctor` output contains actionable freshness state.

### Phase 2

- Objective: Preserve the contract.
- Deliverable: `tools/check_cli_contract.py --surface adoption-host-metadata` covers current, stale, metadata-missing, malformed-manifest, and surface-version runtime cache selection states.
- Exit condition: targeted contract check passes.

## Constraints

- No repo-local plugin install.
- No single SKILL install.
- No Codex runtime cache writes.
- No new dependencies.

## Validation

- Automated checks:
  - `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
  - `git diff --check`
  - `python3 tools/loom.py suite validate --target . --item WI-1721 --json`
  - `python3 tools/loom.py fact-chain --target . --item WI-1721 --json`
- Runtime evidence:
  - `python3 tools/loom.py host doctor --host codex --scope user --json`
- Scenario validation mapping:
  - S1 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S3 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
- Execution ledger validation evidence locator: `.loom/progress/WI-1721.md`

## Test Strategy

- Regression coverage to add or preserve: extend existing adoption host metadata surface only.
- Cases intentionally not automated: real Codex app reload; covered by read-only runtime-cache detection and reload guidance.
- Acceptance validation mapping:
  - A1 -> test evidence: `assert_codex_payload_readback_contract`
  - A2 -> test evidence: `assert_codex_payload_readback_contract`
  - A3 -> test evidence: `assert_codex_payload_readback_contract`
  - A4 -> test evidence: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`

## Subagent Output Integration

- Owned outputs: none; no subagent writes used.
- Integration owner: main agent.
- Handoff notes locator: none.

## Dependencies

- Blocking inputs: none.
- Required coordination: follow-up issues #1715/#1716 consume this output.
- Rollback boundary: `tools/loom.py`, `tools/check_cli_contract.py`, WI-1721 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is not required for this issue-scoped CLI host readback change
- [x] Story business semantics are not required for this issue-scoped CLI host readback change
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
