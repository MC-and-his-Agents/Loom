# WI-1742 Spec

## Suite Contract

- Suite path: full
- Suite index locator: .loom/specs/WI-1742/suite-index.md
- Consumes:
  - Work Item / FR locator: .loom/work-items/WI-1742.md; https://github.com/MC-and-his-Agents/Loom/issues/1742
  - Story Readiness consumed state: not required; issue #1742 provides the acceptance contract.
  - Story scenario locator: scenarios are authored below.
  - Story Business Confirmation consumed state: not required.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: `tools/check_cli_contract.py --fixture-group ship-wrapper`.
- Locator:
  - Spec locator: .loom/specs/WI-1742/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1742.
  - Freshness rule: re-run after ship apply, closeout policy, or closeout readback fixture changes.

## Goal

WI-1742 makes inline / host-only closeout behavior mechanically covered by the ship wrapper regression suite. Ordinary light and standard delivery should be able to use `loom ship --apply` without learning a separate closeout PR path, while release, reinforced, or versioned terminal carrier cases still block and point to an explicit closeout route.

## Scope

- In scope:
  - Add ship-wrapper regression coverage for light ordinary PR host-only closeout.
  - Add ship-wrapper regression coverage for standard ordinary PR host-only closeout.
  - Assert post-merge host reconciliation and closeout readback consume PR merged, issue closed, merge commit, and target branch contains merge commit facts.
  - Assert release and versioned terminal carrier input block before merge and point to explicit closeout queue path.
- Out of scope:
  - Real release publication.
  - GitHub permission model changes.
  - Changes to #1743 release behavior.

## Key Scenarios

### Scenario S1

Given a light ordinary PR whose gates, controlled merge check, and metadata repair chain pass

When `loom ship --apply` executes the controlled merge

Then it runs host reconciliation and closeout check, confirms issue closed and PR merged, and does not create a closeout PR.

### Scenario S2

Given a standard ordinary PR with no release, reinforced, or versioned terminal triggers

When `loom ship --apply` completes merge

Then it still consumes the host-only closeout readback and does not route through the closeout queue.

### Scenario S3

Given a PR whose metadata includes release or versioned terminal carrier triggers

When `loom ship --apply` reaches closeout policy admission

Then it blocks before merge and reports the explicit closeout queue path as the next action.

## Behavior Evidence

- Story scenario mapping: scenarios are authored in this spec.
- Story readiness locator or not-required rationale: not required; issue #1742 acceptance is sufficient.
- Story business confirmation locator or not-required rationale: not required.
- Scenario coverage:
  - S1 -> `assert_ship_inline_host_only_closeout_e2e_contract` light case.
  - S2 -> `assert_ship_inline_host_only_closeout_e2e_contract` standard case.
  - S3 -> `assert_ship_inline_host_only_closeout_e2e_contract` release and versioned terminal blockers.
- Expected evidence locator: .loom/specs/WI-1742/evidence-map.md
- Freshness rule: review consumes validation at the current PR head only.
- Execution ledger acceptance locator: .loom/progress/WI-1742.md

## Exceptions And Boundaries

- Failure modes: missing PR gate, failed carrier refresh, failed shadow parity, or failed closeout readback remains blocking.
- Operational boundaries: the fixture must not perform real GitHub writes, releases, or npm operations.
- Rollback or fallback expectations: remove the added fixture assertions and WI-1742 carrier files if the PR is abandoned before review consumption.

## Acceptance Criteria

- [x] A1: Light ordinary `ship --apply` fixture completes host-only closeout without creating a closeout PR.
- [x] A2: Standard ordinary `ship --apply` fixture completes host-only closeout without creating a closeout PR.
- [x] A3: Host reconciliation and closeout check consume issue closed, PR merged, merge commit, and target branch facts.
- [x] A4: Release and versioned terminal carrier input block before merge and point to explicit closeout queue path.
- [x] A5: Targeted validation evidence is identified for review, merge-ready, and closeout.
