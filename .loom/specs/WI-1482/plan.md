# WI-1482 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1482 is a bounded helper-layer budget-protection Work Item with deterministic focused tests and no external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent issues #1483/#1484/#1485, and issue closeout may consume this minimal suite plus focused test evidence for the reusable budget contract only. recheck condition: require full suite artifacts if scope expands into command-by-command integration, plugin/skill protocol changes, release execution, security/privacy policy, or external-visible host writes.
- Consumes:
  - Spec locator: .loom/specs/WI-1482/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A3
  - Story Readiness consumed state: issue body is sufficient for this helper-layer hardening item.
  - Story Business Confirmation consumed state: no external business semantics.
- Produces:
  - Validation strategy by scenario: focused unit tests plus py_compile/diff checks.
  - Test strategy by acceptance: `test/output_envelope_test.py`.
  - Fresh verification evidence expectation: rerun focused checks at current head before PR gate.
- Locator:
  - Plan locator: .loom/specs/WI-1482/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1482/spec.md; issue #1482.
  - Freshness rule: recheck after helper API or budget default changes.

## Implementation Goal

- Add default and configurable budget protection to the reusable output helper layer.
- Defer command-by-command consumption to dependent issues.

## Phases

### Phase 1

- Objective: Add default budget constants, environment override, summary target truncation, and explicit full output mode.
- Deliverable: `tools/loom.py` helper behavior.
- Exit condition: helpers are importable and focused tests exercise default, configured, and full output paths.

### Phase 2

- Objective: Add large payload regression coverage and carriers.
- Deliverable: `test/output_envelope_test.py` and Loom suite/carrier files.
- Exit condition: focused tests, py_compile, and diff check pass.

## Constraints

- Do not change command pass/fail semantics.
- Do not restore repo-local runtime/plugin/skills paths.
- Do not make output artifacts authoritative truth carriers.
- Keep configuration minimal and local to the helper contract.

## Validation

- Automated checks:
  - `python3 test/output_envelope_test.py`
  - `python3 -m unittest discover -s test -p 'output_envelope_test.py'`
  - `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`
  - `git diff --check`
- Manual checks: inspect that default and configured envelopes omit large diagnostic payloads.
- Runtime evidence: not required for this helper-only slice.
- Behavior evidence: .loom/specs/WI-1482/evidence-map.md
- Fresh verification evidence: rerun checks after any helper changes.
- Scenario validation mapping:
  - S1 -> automated: `test_default_budget_keeps_large_payload_out_of_stdout`
  - S2 -> automated: `test_budget_can_be_configured_with_env`
  - S3 -> automated: `test_explicit_full_output_mode_returns_payload`

## Test Strategy

- TDD or test-first expectation: focused tests define the reusable budget contract before command integration.
- Regression coverage to add or preserve: default large payload, configurable budget values, explicit full output mode.
- Cases that are intentionally not automated: integration into every high-noise command; covered by dependent issues.
- How passing tests or equivalent checks will be captured as test evidence: .loom/specs/WI-1482/evidence-map.md and final PR validation summary.
- Acceptance test mapping:
  - A1 -> test evidence: `test_default_budget_keeps_large_payload_out_of_stdout`
  - A2 -> test evidence: `test_budget_can_be_configured_with_env`
  - A3 -> test evidence: `test_explicit_full_output_mode_returns_payload`

## Dependencies

- Blocking inputs: #1481 merged helper contract.
- Required coordination: dependent issues #1483, #1484, and #1485 consume the configured budget helper.
- Rollback boundary: revert `tools/loom.py` budget additions, focused tests, and WI-1482 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by the issue body for this helper-layer item
- [x] Story business semantics do not apply to this helper-layer item
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
