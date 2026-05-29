# Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: #1147 is a minimal happy path regression fixture Work Item that proves minimal suite automation passes without requiring full-path artifacts; consumer boundary: source/installed regression checks, spec review, review, merge-ready, closeout, and #1145 FR progress may consume the fixture evidence but must not treat skipped full-path artifacts as completed; recheck condition: #1147 starts testing full-path artifacts or #1145 advances to #1148 full suite fixture.
- Consumes:
  - Work Item / FR locator: #1147 / #1145
  - Story Readiness source: GitHub Work Item body is the scoped carrier.
  - Story scenario source: scenarios are authored below.
  - Story Business Confirmation source: governance regression only; no business-semantics carrier.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: source and installed regression checks fail if the minimal happy path stops passing suite validation, evidence validation, or carrier validation.
- Locator:
  - Spec locator: .loom/specs/WI-1147/spec.md
- Provenance:
  - Source issue / PR / doc locator: #1147, #1145, #1052, docs/methodology/harness/full-spec-suite-cli-surface.md, docs/methodology/templates/evidence-map.md, docs/methodology/harness/task-carrier-contract.md
  - Freshness rule: re-run contract and source-self fixture checks after changing minimal happy path fixture assertions.

## Goal

- Prove a valid minimal suite path can pass source and installed governance automation checks.
- Keep the fixture scoped to minimal path behavior and leave full-path and negative fixtures to later #1145 Work Items.

## Scope

- In scope: a minimal suite fixture with valid `spec.md`, `plan.md`, legal full-artifact skip rationale, evidence-map, execution-breakdown, task-carrier, and source/installed validator pass assertions.
- Out of scope: full suite happy path, missing artifact and invalid skip-rationale negative fixtures, stale evidence and host conflict fixtures, scaffold dry-run/apply fixtures, generated skills parity fixtures, PR gate/merge-ready/closeout integration fixtures, host writes, or new product behavior.

## Key Scenarios

### Scenario S1

Given
- a minimal suite fixture has valid `spec.md` and `plan.md`
- skipped full-path artifacts have a legal skip rationale with consumer boundary and recheck condition

When
- `loom suite validate --target <fixture> --item <item> --json` runs

Then
- the validator returns pass, records `suite_path: minimal`, and reports no missing inputs, blocking gaps, or advisory gaps.

### Scenario S2

Given
- the same minimal suite fixture includes behavior, test, and fresh verification evidence rows

When
- `loom suite evidence validate --target <fixture> --item <item> --json` runs

Then
- the validator returns pass and consumes the evidence-map locator without treating CLI output as Work Item or closeout truth.

### Scenario S3

Given
- the same minimal suite fixture includes a primary task-carrier row linked to the Work Item, execution breakdown, spec, and plan

When
- `loom suite carrier validate --target <fixture> --item <item> --json` runs

Then
- the validator returns pass and keeps carrier status as tracking-only evidence.

## Acceptance Criteria

- A1: `tools/check_cli_contract.py` contains a minimal happy path fixture that validates suite, evidence, and carrier surfaces together.
- A2: `loom_check` source-self daily execution fixture explicitly verifies the minimal suite happy path before source review-run consumption.
- A3: `loom_check` installed pre-merge fixture explicitly verifies the minimal suite happy path before installed review/merge-ready consumption.
- A4: Source/generated runtime copies remain synchronized and no `/speckit.*` command or `.specify/` layout is introduced.

## Behavior Evidence

- Story scenario mapping: S1-S3 are issue-scoped and authored in this file.
- Story readiness locator: #1147 body is the readiness source.
- Story business confirmation locator: none required for governance regression behavior.
- Scenario coverage:
  - S1 -> expected behavior evidence locator: `tools/check_cli_contract.py` minimal happy path fixture and `require_minimal_suite_happy_path_validation`.
  - S2 -> expected behavior evidence locator: `tools/check_cli_contract.py` evidence validation assertion and `loom_check` source/installed helper.
  - S3 -> expected behavior evidence locator: `tools/check_cli_contract.py` carrier validation assertion and `loom_check` source/installed helper.
- Expected evidence locator: .loom/specs/WI-1147/evidence-map.md
- Freshness rule: evidence is fresh only after local contract/source checks pass on the current head.
- Execution ledger acceptance locator: .loom/progress/WI-1147.md
- Behavior-bearing change rationale: E2E regression now proves the minimal suite happy path across source and installed governance fixtures.
