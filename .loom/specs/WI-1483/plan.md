# WI-1483 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1483 is a bounded CLI output contract Work Item using existing output envelope and budget helpers. consumer boundary: suite validate, review, PR gate, merge-ready, dependent #1484/#1485, and issue closeout. recheck condition: require full suite artifacts if scope expands beyond fact-chain/status/shadow-parity wrappers.
- Consumes:
  - Spec locator: .loom/specs/WI-1483/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A4
  - Story Readiness consumed state: issue #1483 body and v0.17.0 amendment.
  - Story Business Confirmation consumed state: no external business semantics.
- Produces:
  - Validation strategy by scenario: unit tests, real stdout probes, and CLI contract.
  - Test strategy by acceptance: output envelope tests plus contract consumer full-output updates.
  - Fresh verification evidence expectation: rerun focused checks at current head before PR gate.
- Locator:
  - Plan locator: .loom/specs/WI-1483/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1483/spec.md; issue #1483.
  - Freshness rule: recheck after output wrapper, budget, artifact locator, or PR metadata changes.

## Implementation Goal

- Wrap the target global CLI commands in default agent-safe output without changing their underlying pass/block semantics.
- Add `loom shadow-parity` as the supported global command surface for shadow parity reads.

## Phases

### Phase 1

- Objective: Wire default summary/artifact output for target commands.
- Deliverable: `tools/loom.py` changes for `status`, `fact-chain`, and `shadow-parity`.
- Exit condition: real command probes show default stdout below 16 KiB and full-output remains available.

### Phase 2

- Objective: Update tests and machine consumers.
- Deliverable: output envelope tests and CLI contract full-output consumer updates.
- Exit condition: output tests, py_compile, real probes, and full CLI contract pass.

## Constraints

- Do not change fact-chain, status, or shadow parity judgment logic.
- Do not alter flow gate command families owned by #1484.
- Do not remove full JSON access for existing scripts.
- Do not restore repo-local runtime, plugin, or skills installation paths.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `git diff --check`
- Runtime evidence:
  - `python3 tools/loom.py fact-chain --target . --json`: 1150 bytes
  - `python3 tools/loom.py status --target . --json`: 1138 bytes, expected block for current repo state
  - `python3 tools/loom.py shadow-parity --target . --surface all --blocking --json`: 1132 bytes
  - `python3 tools/loom.py fact-chain --target . --json --full-output`: 40892 bytes
- Behavior evidence: .loom/specs/WI-1483/evidence-map.md
- Fresh verification evidence: rerun checks after carrier, review, or head changes.
- Scenario validation mapping:
  - S1 -> automated: `test/output_envelope_test.py` and real default stdout budget probes validate bounded summary/artifact output.
  - S2 -> automated: `test/output_envelope_test.py` and `loom fact-chain --full-output` probe validate explicit raw output.
  - S3 -> automated: `tools/check_cli_contract.py` validates machine consumers request `--full-output`.

## Test Strategy

- TDD or test-first expectation: extend output envelope unit tests before merge-ready consumption.
- Regression coverage to add or preserve: full-output escape hatch and contract consumers that need nested JSON.
- Cases intentionally not automated: human readability of the summary; covered by review.
- Acceptance test mapping:
  - A1 -> test evidence: real stdout probes and default budget unit tests.
  - A2 -> test evidence: artifact existence checks and `--full-output` unit test/probe.
  - A3 -> test evidence: output envelope unit tests for gaps, counts, and locators.
  - A4 -> test evidence: `tools/check_cli_contract.py`.

## Dependencies

- Blocking inputs: #1481 output envelope contract and #1482 budget helper are merged.
- Required coordination: #1484 consumes the same pattern for flow gate commands; #1485 consumes unified default entry behavior.
- Rollback boundary: revert `tools/loom.py`, `test/output_envelope_test.py`, `tools/check_cli_contract.py`, and WI-1483 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by issue #1483
- [x] Story business semantics do not apply
- [x] Validation path is defined
- [x] BDD scenarios map to validation
- [x] Risks and dependencies are explicit
