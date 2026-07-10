# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1943
  - Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; this is a gate bug fix from observed PR #1942 evidence.
  - Story scenario locator, or not-required rationale: not required; behavior is covered by CLI contract fixtures.
  - Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; no user-facing product semantics change.
- Produces:
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1, A2
  - Behavior evidence expectation: targeted controlled-merge and governance-closeout fixtures.
- Locator:
  - Spec locator: .loom/specs/WI-1943/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1943; PR #1942 local and hosted gate replay.
  - Freshness rule: stale if terminal closeout PR gate payload schema, closeout role semantics, or controlled-merge retained gate consumption changes.

## Goal

Controlled merge and closeout must consume terminal closeout carrier PR evidence that already passed PR gate.

## Scope

- In scope: terminal closeout carrier PR retained-gate consumption and closeout readback fallback to implementation PR host checks when no merge-ready execution_attempt exists.
- Out of scope: relaxing implementation PR merge checkpoint requirements, changing GitHub rulesets, or broad closeout redesign.

## Key Scenarios

### Scenario S1

Given a retained PR gate result with `terminal_closeout_consumption.result == pass` and `closeout_specific_gate.closeout_pr_allowed == true`

When controlled merge consumes that retained gate for the same PR head

Then it accepts the terminal closeout path without requiring the embedded normal merge checkpoint to pass.

### Scenario S2

Given a final closeout carrier PR and a merged implementation PR with passing host checks

When closeout readback has no retained successful `merge-ready` execution_attempt

Then it consumes the implementation PR host checks as legacy merge-ready evidence for that terminal closeout carrier PR.

## Acceptance Criteria

- A1: Controlled merge still blocks ordinary retained PR gates whose merge checkpoint fails unless terminal closeout consumption also passed.
- A2: Closeout readback passes for terminal closeout carrier PRs without retained merge-ready attempts when implementation PR host checks are fresh and passing.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `python3 tools/check_cli_contract.py --surface controlled-merge`
  - S2 -> `python3 tools/check_cli_contract.py --surface governance-closeout`
- Expected evidence locator: tools/check_cli_contract.py
- Freshness rule: rerun targeted surfaces after touching `loom_flow.py` gate/closeout consumption.
