# Spec

## Suite Contract

- Suite path: full
- Consumes:
  - Work Item / FR locator: #1148 / #1145
  - Story Readiness source: GitHub Work Item body is the scoped carrier.
  - Story scenario source: scenarios are authored below.
  - Story Business Confirmation source: governance regression only; no business-semantics carrier.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: source and installed regression checks fail if the full suite happy path stops passing suite validation, evidence validation, or carrier validation.
- Locator:
  - Spec locator: .loom/specs/WI-1148/spec.md
- Provenance:
  - Source issue / PR / doc locator: #1148, #1145, #1052, docs/methodology/harness/full-spec-suite-cli-surface.md, docs/methodology/templates/spec-suite.md, docs/methodology/templates/evidence-map.md, docs/methodology/harness/task-carrier-contract.md
  - Freshness rule: re-run contract and source-self fixture checks after changing full suite happy path fixture assertions.

## Goal

- Prove a valid full suite path can pass source and installed governance automation checks.
- Keep the fixture scoped to full happy path behavior and leave negative, scaffold, parity, and PR-gate integration fixtures to later #1145 Work Items.

## Scope

- In scope: a full suite fixture with `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, `readiness-checklist.md`, `evidence-map.md`, `consistency-analysis.md`, `execution-breakdown.md`, `task-carrier.md`, and source/installed validator pass assertions.
- Out of scope: missing artifact and invalid skip-rationale negative fixtures, stale evidence and host conflict fixtures, scaffold dry-run/apply fixtures, generated skills parity fixtures, PR gate/merge-ready/closeout integration fixtures, host writes, or new product behavior.

## Scenarios

### Scenario S1

Given
- a full suite fixture has a suite-index path decision
- required and conditional artifacts are present

When
- `loom suite validate --target <fixture> --item <item> --json` runs

Then
- the validator returns pass, records `suite_path: full`, and reports no missing inputs, blocking gaps, or advisory gaps.

### Scenario S2

Given
- the same full suite fixture includes behavior, test, and fresh verification evidence rows

When
- `loom suite evidence validate --target <fixture> --item <item> --json` runs

Then
- the validator returns pass and consumes the evidence-map locator without treating CLI output as Work Item or closeout truth.

### Scenario S3

Given
- the same full suite fixture includes a primary task-carrier row linked to the Work Item, execution breakdown, spec, and plan

When
- `loom suite carrier validate --target <fixture> --item <item> --json` runs

Then
- the validator returns pass and keeps carrier status as tracking-only evidence.

## Acceptance Criteria

- A1: `tools/check_cli_contract.py` contains a full happy path fixture that validates suite, evidence, and carrier surfaces together.
- A2: `loom_check` source-self daily execution fixture explicitly verifies the full suite happy path before source review-run consumption.
- A3: `loom_check` installed pre-merge fixture explicitly verifies the full suite happy path before installed review/merge-ready consumption.
- A4: Source/generated/runtime copies remain synchronized and no `/speckit.*` command or `.specify/` layout is introduced.

## Behavior Evidence

- Story scenario mapping: S1-S3 are issue-scoped and authored in this file.
- Story readiness locator: #1148 body is the readiness source.
- Story business confirmation locator: none required for governance regression behavior.
- Scenario coverage:
  - S1 -> expected behavior evidence locator: `tools/check_cli_contract.py` full happy path fixture and `require_full_suite_happy_path_validation`.
  - S2 -> expected behavior evidence locator: `tools/check_cli_contract.py` evidence validation assertion and `loom_check` source/installed helper.
  - S3 -> expected behavior evidence locator: `tools/check_cli_contract.py` carrier validation assertion and `loom_check` source/installed helper.
- Expected evidence locator: .loom/specs/WI-1148/evidence-map.md
- Freshness rule: evidence is fresh only after local contract/source checks pass on the current head.
- Execution ledger acceptance locator: .loom/progress/WI-1148.md
- Behavior-bearing change rationale: E2E regression now proves the full suite happy path across source and installed governance fixtures.
