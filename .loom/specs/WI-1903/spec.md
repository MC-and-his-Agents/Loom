# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: issue #1903 / FR #1902 / Phase #1888
  - Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; #1903 is scoped by the GitHub Work Item and existing workstation registry contract.
  - Story scenario locator, or not-required rationale: not required; scenarios below are direct CLI planning scenarios.
  - Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; internal workstation orchestration behavior.
- Produces:
  - Scenario ids / locators: S1-S4 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: focused CLI contract fixture proves plan-only behavior and classification coverage.
- Locator:
  - Spec locator: .loom/specs/WI-1903/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1903; docs/adoption/workstation-registry-contract.md; docs/evidence/fixtures/workstation-registry-fixtures.json.
  - Freshness rule: Recheck when workstation registry schema, version freshness, host plugin readback, or workstation upgrade planning changes.

## Goal

Add a machine-level upgrade planner that lets an operator see the Loom CLI/plugin refresh steps and each registered repository's adoption classification before any workstation or repository mutation occurs.

## Scope

- Implement `loom workstation upgrade --plan --to <version> --json`.
- Include a `machine_only` plan for npm CLI refresh, Codex plugin refresh/register, and host doctor readback.
- Classify registered repositories as `repo_noop`, `repo_auto_commit_candidate`, `repo_pr_required`, or `blocked`.
- Fail closed when registry path, remote hash, id, schema, or unknown adoption state makes mutation planning unsafe.
- Keep `--apply`, freshness caching, detailed machine refresh semantics, and legacy migration apply in later WIs.

## Key Scenarios

### Scenario S1

Given the workstation registry is empty

When the operator runs `loom workstation upgrade --plan --to <version> --json`

Then the command returns a read-only `machine_only` plan and no repository plans.

### Scenario S2

Given registered metadata-only repositories at the target version and below the target version

When the operator runs the plan command

Then current metadata-only repositories are `repo_noop` and older metadata-only repositories are `repo_auto_commit_candidate`.

### Scenario S3

Given registered legacy or repo-local-wrapper repositories

When the operator runs the plan command

Then those repositories are classified `repo_pr_required` and no repository mutation is performed.

### Scenario S4

Given a registered repository entry has path or identity drift

When the operator runs the plan command

Then the command returns `block`, includes a `blocked` repository plan, and reports repair guidance.

## Acceptance Criteria

- [x] A1: `loom workstation upgrade --plan --to <version> --json` is implemented and non-mutating.
- [x] A2: Empty registry output includes a `machine_only` plan and no repository plans.
- [x] A3: Focused fixtures cover `repo_noop`, `repo_auto_commit_candidate`, `repo_pr_required`, and `blocked`.
- [x] A4: Plan output preserves registry fail-closed behavior for blocking entries.
- [x] A5: Runtime fixture/hash drift exposed by validation is fixed without changing product behavior.
