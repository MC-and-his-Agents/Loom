# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: .loom/specs/WI-1716/spec.md
  - Implementation contract locator: .loom/specs/WI-1716/implementation-contract.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A4
  - Story Readiness consumed state: not required
  - Story Business Confirmation consumed state: not required
- Produces:
  - Validation strategy by scenario: targeted CLI contract checks and direct JSON assertions inside `adoption-host-metadata`.
  - Test strategy by acceptance: extend the existing isolated Codex workstation fixture.
  - Fresh verification evidence expectation: local validation summary before PR and PR head readback before merge-ready.
- Locator:
  - Plan locator: .loom/specs/WI-1716/plan.md
- Provenance:
  - Source spec / issue locator: .loom/specs/WI-1716/spec.md; issue #1716
  - Freshness rule: Re-run validation after any change to `tools/loom.py`, `tools/check_cli_contract.py`, or `docs/adoption/global-cli-user-plugin-contract.md`.

## Implementation Goal

Convert stale plugin payload diagnosis into a short, machine-readable refresh plan that names the correct `loom host ...` commands or reload/readback step.

## Deferred Items

- Broad fixture inventory belongs to #1717.
- v0.19.0 release closeout belongs to #1718.

## Not Required Items

- Legacy installer retirement is already superseded by #1732.
- Direct runtime cache mutation is not allowed.

## Phases

### Phase 1

- Objective: Add structured refresh guidance.
- Deliverable: `plugin_payload_refresh_guidance()` and extended `cli-plugin-freshness` action fields.
- Exit condition: stale plugin payload cases expose apply/readback/reload guidance.

### Phase 2

- Objective: Cover the guidance contract.
- Deliverable: focused adoption host metadata contract checks for stale marketplace, stale runtime, and repaired readback.
- Exit condition: target surface and diff checks pass.

### Phase 3

- Objective: Document the refresh boundary.
- Deliverable: adoption contract section naming `loom host install/register/doctor` and Codex reload behavior.
- Exit condition: docs do not mention legacy installer as a primary path.

## Constraints

- Keep target `loom install` / `loom upgrade` scoped to repository installed-state.
- Do not mutate Codex runtime cache directly.
- Do not restore single SKILL installation.
- Keep root CLI version, plugin surface version, contract version, and plugin payload version separate.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - `python3 tools/loom.py suite validate --target . --item WI-1716 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1716 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1716 --json`
  - `python3 tools/loom.py fact-chain --target . --item WI-1716 --json`
  - `git diff --check`
- Runtime evidence: local command output summarized in .loom/progress/WI-1716.md.
- Behavior evidence: .loom/specs/WI-1716/evidence-map.md.
- Scenario validation mapping:
  - S1 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S2 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`
  - S3 -> automated validation: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`

## Test Strategy

- Regression coverage: extend the existing `adoption-host-metadata` surface.
- Cases intentionally not automated: real Codex Desktop reload; simulated by replacing the isolated runtime cache with the registered marketplace source.
- Acceptance validation mapping:
  - A1 -> test evidence: stale marketplace `cli-plugin-freshness.apply_commands`
  - A2 -> test evidence: stale marketplace `cli-plugin-freshness.apply_commands`
  - A3 -> test evidence: stale runtime `refresh_guidance.reload_required`
  - A4 -> test evidence: host doctor readback after host install/register and simulated reload

## Subagent Output Integration

- Owned outputs: none; no subagent output is integrated in this Work Item.
- Integration owner: main agent.
- Handoff notes locator: none.

## Dependencies

- Blocking inputs: #1715 freshness action is merged and closed.
- Required coordination: #1717 consumes this guidance for broader fixture coverage.
- Rollback boundary: revert WI-1716 PR only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is not required for this issue-scoped CLI guidance change
- [x] Story business semantics are not required for this issue-scoped CLI guidance change
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
