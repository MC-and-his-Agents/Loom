# WI-1487 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1487 is a bounded docs/contract Work Item for thread rotation and handoff rules, with no external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent issue #1486, and issue closeout may consume this minimal suite plus focused documentation validation for the thread handoff contract only. recheck condition: require full suite artifacts if scope expands into scheduler behavior, CLI implementation, plugin command examples, security/privacy policy, or external-visible host writes.
- Consumes:
  - Spec locator: .loom/specs/WI-1487/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A4
  - Story Readiness consumed state: issue body and dependency update are sufficient for this docs/contract item.
  - Story Business Confirmation consumed state: no external business semantics.
- Produces:
  - Validation strategy by scenario: documentation mirror checks plus fact-chain and shadow parity checks.
  - Test strategy by acceptance: generated tree drift check, suite validation, and carrier validation.
  - Fresh verification evidence expectation: rerun focused checks at current head before PR gate.
- Locator:
  - Plan locator: .loom/specs/WI-1487/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1487/spec.md; issue #1487.
  - Freshness rule: recheck after thread rotation rule, handoff package field, or mirror changes.

## Implementation Goal

- Update the recovery model and handoff output contract so future agents can rotate threads cleanly without consuming noisy old conversation turns by default.

## Phases

### Phase 1

- Objective: Add thread rotation triggers, handoff package fields, artifact locator rules, and new-thread read boundaries.
- Deliverable: recovery model and handoff output contract documentation.
- Exit condition: documentation states the bounded summary/artifact locator relationship and v0.17.0 runtime boundary.

### Phase 2

- Objective: Synchronize source/generated/plugin mirrors and Loom carriers.
- Deliverable: source docs, generated skill references, plugin payload mirrors, suite files, progress/status/review carriers.
- Exit condition: generated-tree drift, fact-chain, shadow parity, suite validate, evidence validate, and carrier validate checks pass.

## Constraints

- Do not implement a scheduler.
- Do not update command examples owned by #1486.
- Do not change CLI output behavior owned by #1483/#1484.
- Do not restore repo-local plugin/runtime/skills paths, single-skill package distribution, or old installer compatibility.
- Do not make diagnostic artifacts authoritative truth carriers.

## Validation

- Automated checks:
  - `git diff --check`
  - `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`
  - `python3 tools/loom.py fact-chain --target . --json`
  - `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
  - `python3 tools/skills_surface.py check --surface generated-tree-drift`
  - `python3 tools/loom.py suite validate --target . --item WI-1487 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1487 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1487 --json`
- Manual checks: inspect that no repo-local runtime/plugin/skills installation path is introduced.
- Runtime evidence: no runtime evidence required for this docs/contract slice.
- Behavior evidence: .loom/specs/WI-1487/evidence-map.md
- Fresh verification evidence: rerun checks after any documentation, carrier, or mirror changes.
- Scenario validation mapping:
  - S1 -> structural check: recovery model documentation includes thread rotation trigger rules.
  - S2 -> structural check: recovery model documentation and handoff output contract include new-thread consumption boundaries.
  - S3 -> structural check: handoff output contract includes artifact locator rules and v0.17.0 runtime boundary wording.

## Test Strategy

- TDD or test-first expectation: docs/contract freeze uses structural validation and review rather than new unit tests.
- Regression coverage to add or preserve: generated-tree drift and suite carrier validation.
- Cases that are intentionally not automated: semantic readability of documentation; covered by review.
- How passing tests or equivalent checks will be captured as test evidence: .loom/specs/WI-1487/evidence-map.md and final PR validation summary.
- Acceptance test mapping:
  - A1 -> structural check: recovery model thread rotation triggers.
  - A2 -> structural check: handoff output contract `thread_rotation_package`.
  - A3 -> structural check: recovery model new-thread consumption boundary.
  - A4 -> structural check: handoff output contract artifact boundary and no repo-local runtime path wording.

## Dependencies

- Blocking inputs: #1481 output envelope contract is merged; #1482 budget helper is merged for artifact/bounded summary assumptions.
- Required coordination: #1486 consumes these handoff rules when updating Codex user-level plugin payload text.
- Rollback boundary: revert recovery model, handoff output contract, mirror docs, and WI-1487 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by the issue body and dependency update
- [x] Story business semantics do not apply to this docs/contract item
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations are covered by structural documentation checks for this docs/contract item
- [x] Risks and dependencies are explicit
