# WI-1482 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1482 is a bounded helper-layer budget-protection Work Item with deterministic focused tests and no external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent issues #1483/#1484/#1485, and issue closeout may consume this minimal suite plus focused test evidence for the reusable budget contract only. recheck condition: require full suite artifacts if scope expands into command-by-command integration, plugin/skill protocol changes, release execution, security/privacy policy, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1482
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue body is the planning source for this hardening item.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A3 in this file.
  - Behavior evidence expectation: focused unit tests in `test/output_envelope_test.py`.
- Locator:
  - Spec locator: .loom/specs/WI-1482/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1482.
  - Freshness rule: recheck after changes to `tools/loom.py` output budget helpers.

## Goal

- Add configurable agent-safe stdout budget protection to the global `loom` CLI helper layer.
- Preserve explicit full output mode for human debugging.

## Scope

- In scope: default stdout budget, summary target, environment override, explicit full output bypass, and large-payload regression tests.
- Out of scope: wiring every high-noise command, changing gate semantics, release execution, repo-local runtime/plugin/skills compatibility.

## Key Scenarios

### Scenario S1

Given a payload exceeds the default agent-safe stdout budget
When Loom builds the default agent-safe payload
Then stdout contains only a bounded envelope and artifact locator, not the full diagnostic payload.

### Scenario S2

Given an operator configures budget values
When Loom builds an over-budget payload
Then the envelope reports and honors the configured stdout budget and summary target.

### Scenario S3

Given an operator explicitly requests full output mode
When Loom builds an agent-safe payload
Then Loom returns the original full payload for debugging.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `test_default_budget_keeps_large_payload_out_of_stdout`
  - S2 -> `test_budget_can_be_configured_with_env`
  - S3 -> `test_explicit_full_output_mode_returns_payload`
- Expected evidence locator: .loom/specs/WI-1482/evidence-map.md
- Freshness rule: evidence must be rerun after output budget helper changes.

## Exceptions And Boundaries

- Failure modes: invalid environment override falls back to the safe default budget.
- Operational boundaries: full output is explicit helper mode only; default agent-facing output remains bounded.
- Rollback or fallback expectations: revert helper additions and focused tests if later command integration chooses a different budget surface.

## Acceptance Criteria

- [x] A1: Default large payload does not exceed the agent-safe stdout budget.
- [x] A2: Budget and summary target can be configured by explicit values or environment override.
- [x] A3: Explicit full output mode still returns the original full payload.
