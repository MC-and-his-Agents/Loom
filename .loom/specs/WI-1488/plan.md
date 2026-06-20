# WI-1488 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1488 is a bounded documentation/help/migration item. consumer boundary: review, PR gate, #1658 release readiness, #1489 final closeout, and issue closeout may consume this minimal suite and focused docs checks. recheck condition: require full suite artifacts if scope expands into runtime implementation, package release, downstream migration, or external host writes.
- Consumes:
  - Spec locator: .loom/specs/WI-1488/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: issue #1488 body and v0.17.0 baseline.
  - Story Business Confirmation consumed state: not_applicable.
- Produces:
  - Validation strategy by scenario: focused docs/help text inspection, CLI help JSON readback, targeted legacy recommendation search, suite validation, and diff check.
  - Test strategy by acceptance: structural grep/readback checks plus review.
  - Fresh verification evidence expectation: rerun at current PR head before review and PR gate.
- Locator:
  - Plan locator: .loom/specs/WI-1488/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1488/spec.md; issue #1488.
  - Freshness rule: recheck after README, docs/adoption, CLI command matrix, or WI carrier changes.

## Implementation Goal

- Update user-facing docs and help-facing command matrix text to match the context-safe runtime and v0.17.0 support boundary.
- Defer release execution, final milestone closeout, downstream repository migration, and runtime/skill implementation to their owning issues.

## Phases

### Phase 1

- Objective: Author WI-1488 carriers and update docs/help-facing contracts.
- Deliverable: Work Item, progress, minimal suite, task carrier, README/adoption/CLI matrix text updates.
- Exit condition: docs describe output modes and metadata-only/global CLI/plugin boundary without current-path legacy recommendations.

### Phase 2

- Objective: Validate docs consistency and prepare PR evidence.
- Deliverable: suite checks, CLI help readback, targeted legacy recommendation search, and diff check.
- Exit condition: validation evidence is current and ready for review/PR gate.

## Constraints

- Do not publish #1658 or mutate release/tag/npm/GitHub Release state.
- Do not implement #1489 final regression closeout.
- Do not migrate downstream repositories or write runtime/plugin/skills payloads into target repositories.
- Do not change CLI runtime behavior, output budget constants, artifact writer implementation, or skill payload source.
- Do not treat deprecated installer anchors as current compatibility paths.

## Validation

- Automated checks:
  - `python3 tools/loom.py help --json`
  - `python3 tools/loom.py suite validate --target . --item WI-1488 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1488 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1488 --json`
  - targeted `rg` checks for current-path recommendations of repo-local plugin/runtime/skills installs, single-skill package distribution, and old installer paths
  - `git diff --check`
- Manual checks: inspect docs changed only within #1488 scope.
- Runtime evidence: no live runtime evidence required; CLI help JSON readback is enough.
- Behavior evidence: .loom/specs/WI-1488/evidence-map.md
- Scenario validation mapping:
- S1 -> structural: docs inspection and targeted legacy install search.
- S2 -> structural: CLI help JSON readback and docs output-mode text inspection.
- S3 -> structural: docs inspection against #1658 release acceptance.

## Test Strategy

- TDD or test-first expectation: docs-only change uses structural checks rather than new runtime tests.
- Regression coverage to add or preserve: existing CLI contract checks and metadata-only adoption checks remain in `tools/check_cli_contract.py`; this item adds no new runtime tests.
- Cases intentionally not automated: prose clarity; covered by review.
- Acceptance test mapping:
- A1 -> structural check: docs search.
- A2 -> structural check: docs search.
- A3 -> structural check: CLI help JSON readback plus docs inspection.
- A4 -> structural check: targeted legacy recommendation search.
- A5 -> validation evidence: suite evidence and carrier validation.

## Dependencies

- Blocking inputs: #1481/#1482 output envelope and budget contract, #1484/#1485 global CLI agent-safe behavior, #1486 skill payload update, and #1487 handoff/thread rules are closed.
- Required coordination: #1658 consumes this docs/help/migration wording for release notes and release evidence; #1489 consumes it for final closeout verification.
- Rollback boundary: revert README/adoption/CLI matrix text updates and WI-1488 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by issue #1488
- [x] Story business semantics do not apply
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations are covered by structural checks
- [x] Risks and dependencies are explicit
