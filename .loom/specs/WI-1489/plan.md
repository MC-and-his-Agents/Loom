# WI-1489 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: final closeout consumes existing milestone evidence and does not design new product behavior. consumer boundary: review, PR gate, #1489 closeout, parent #1480, and phase #1476. recheck condition: require full suite artifacts if final closeout expands into implementation, release, or downstream migration work.
- Consumes:
  - Spec locator: .loom/specs/WI-1489/spec.md
  - Scenario ids / locators: S1-S4
  - Acceptance ids / locators: A1-A6
- Produces:
  - Validation strategy by scenario: focused CLI/runtime tests, docs/help/skill checks, release readback, suite/fact-chain/shadow validation, and GitHub issue dependency readback.
  - Fresh verification evidence expectation: update docs/evidence/milestone-11-final-closeout.md at current branch head.

## Phases

### Phase 1

- Objective: Assemble final closeout evidence.
- Deliverable: WI-1489 suite, progress, task carrier, and milestone final closeout evidence.
- Exit condition: local regression matrix passes.

### Phase 2

- Objective: Review and merge closeout evidence PR.
- Deliverable: current-head Loom review record, PR metadata, PR gate, hosted checks, controlled merge.
- Exit condition: main contains WI-1489 closeout evidence.

### Phase 3

- Objective: Close #1489 and parent/phase if eligible.
- Deliverable: issue closeout comments and GitHub state readback for #1489, #1480, and #1476.
- Exit condition: milestone/11 has no open issues.

## Validation

- `python3 test/output_envelope_test.py`
- `python3 tools/loom.py help --json`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit 3e17dd73fb4ccb260ede68e5518b83aa904fb682 --release-judgment release_required --json`
- `python3 tools/loom.py suite validate --target . --item WI-1489 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1489 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1489 --json`
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `git diff --check`

## Scenario Validation Mapping

- S1 -> automated: `python3 test/output_envelope_test.py`; `python3 tools/loom.py help --json`; WI-1489 final closeout evidence.
- S2 -> automated/structural: `python3 tools/loom.py help --json`; `python3 tools/skills_surface.py check`; `python3 tools/check_release_surface.py`; WI-1488 and WI-1658 evidence locators.
- S3 -> structural/manual evidence: #1493 closed state, WI-1495/WI-1496 closeout evidence, and WI-1489 final closeout evidence classify #1493 as identity-binding hardening.
- S4 -> automated/readback: `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit 3e17dd73fb4ccb260ede68e5518b83aa904fb682 --release-judgment release_required --json`; WI-1658 release readiness and goal completion evidence.

## Acceptance Test Mapping

- A1 -> automated: `python3 test/output_envelope_test.py` and `python3 tools/loom.py help --json`.
- A2 -> structural: `python3 tools/loom.py help --json`, release surface checks, and `docs/evidence/milestone-11-final-closeout.md`.
- A3 -> automated: `python3 tools/skills_surface.py check`.
- A4 -> structural/manual evidence: #1493 closeout readback and final closeout evidence classification.
- A5 -> automated/readback: release readback plus `docs/evidence/v0.17.1-release-readiness.md` and `.loom/progress/WI-1658-goal-completion.json`.
- A6 -> manual evidence: #1489 closeout before #1480/#1476 closeout and milestone open issue readback.

## Dependencies

- Blocking inputs: #1482, #1483, #1484, #1485, #1486, #1487, #1488, #1493, and #1658 must be closed and consumed.
- Required coordination: #1489 closes before parent #1480 and phase #1476.
- Rollback boundary: revert only WI-1489 evidence/carrier changes before merge; no release artifacts are changed.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story readiness is covered by issue #1489
- [x] Validation path is defined
- [x] Release evidence dependency is present
