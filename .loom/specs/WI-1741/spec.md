# WI-1741 Spec

## Suite Contract

- Suite path: full
- Suite index locator: .loom/specs/WI-1741/suite-index.md
- Work Item / FR locator: GitHub issue #1741 under parent FR #1734.
- Story Readiness consumed state: not required; issue #1741 provides bounded acceptance.
- Story Business Confirmation consumed state: not required; this is Loom CLI delivery behavior.
- Scenario ids / locators: S1, S2, S3 in this spec.
- Acceptance ids / locators: A1-A5 in this spec.
- Behavior evidence expectation: `tools/check_cli_contract.py --fixture-group ship-wrapper` plus docs contract snippets.
- Spec locator: .loom/specs/WI-1741/spec.md
- Source issue / PR / doc / conversation locator: GitHub issue #1741.
- Freshness rule: stale after ship wrapper, validation profile taxonomy, changed-path readback, or docs contract changes.

## Goal

Make `loom ship` explain the smallest useful validation profile for a PR from changed paths, so ordinary delivery does not default every item to the heaviest validation path.

## Scope

- In scope: `loom ship` dry-run/apply diagnostics, PR changed-path readback, validation profile selection, explicit profile override, and ship docs/contract fixtures.
- Out of scope: repair chain execution (#1739), closeout e2e (#1742), release closeout (#1743), and rewriting `loom_check`.

## Key Scenarios

### Scenario S1

Given a PR changes only docs or deprecated package tombstone surfaces.

When an agent runs `loom ship --json`.

Then the output includes a `validation_profile` diagnostic selecting the light profile and naming the `contract-only` source surface.

### Scenario S2

Given a PR changes runtime, harness, tool, workflow, test, plugin, or generated fixture surfaces.

When an agent runs `loom ship --json`.

Then the output selects full validation and names the full source-surface command.

### Scenario S3

Given a PR is release-oriented or the caller explicitly requests `--validation-profile full`.

When `loom ship` builds its delivery plan.

Then release scope selects release validation, and explicit full override is preserved even when changed paths would otherwise be light.

## Behavior Evidence

- Story scenario mapping: S1-S3 map to ship wrapper contract fixtures.
- Story readiness locator or not-required rationale: not required; issue #1741 acceptance is the bounded source.
- Story business confirmation locator or not-required rationale: not required; no external business workflow changes.
- Scenario coverage:
  - S1 -> `tools/check_cli_contract.py` docs/package tombstone validation profile fixture.
  - S2 -> `tools/check_cli_contract.py` runtime/harness validation profile fixture.
  - S3 -> `tools/check_cli_contract.py` release and explicit override fixtures.
- Expected evidence locator: .loom/specs/WI-1741/evidence-map.md
- Freshness rule: re-run after any `loom ship` wrapper, docs contract, or validation profile mapping change.
- Execution ledger acceptance locator: .loom/specs/WI-1741/spec.md

## Exceptions And Boundaries

- Failure modes: unreadable changed paths must choose safe standard validation instead of under-validating.
- Operational boundaries: ship selection is diagnostic; it reports commands and does not rewrite `loom_check`.
- Rollback or fallback expectations: revert the PR or use explicit `--validation-profile full` if auto classification is wrong.

## Acceptance Criteria

- [x] A1: `ship --dry-run` explains selected validation profile and reason.
- [x] A2: docs/package tombstone paths choose light profile.
- [x] A3: runtime/harness paths choose full profile.
- [x] A4: release scope chooses release profile.
- [x] A5: explicit full profile override is preserved.
