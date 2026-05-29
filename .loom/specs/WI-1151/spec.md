# Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: #1151 is a scaffold mutation boundary regression Work Item that proves scaffold dry-run/apply behavior without requiring a full authored suite for this Work Item; consumer boundary: source/installed regression checks, spec review, review, merge-ready, closeout, and #1145 FR progress may consume the fixture evidence but must not treat skipped full-path artifacts as completed; recheck condition: #1151 starts validating full-path authored content or adds new scaffold artifact types.
- Consumes:
  - Work Item / FR locator: #1151 / #1145
  - Story Readiness source: GitHub Work Item body.
  - Story scenario source: scenarios authored below.
  - Story Business Confirmation source: governance regression only; no business-semantics carrier.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: source and installed checks fail if scaffold dry-run/apply mutation boundaries drift.
- Locator:
  - Spec locator: .loom/specs/WI-1151/spec.md
- Provenance:
  - Source issue / doc locator: #1151, #1145, #1052, docs/methodology/harness/full-spec-suite-cli-surface.md, docs/methodology/templates/spec-suite.md
  - Freshness rule: re-run focused scaffold contract and source-surface checks after changing scaffold fixtures.

## Goal

- Prove `loom suite scaffold` is dry-run by default and writes only contracted suite scaffold artifacts under explicit `--apply`.
- Keep CLI output as fixture evidence only; it does not replace Work Item, review, merge-ready, closeout, or host truth.

## Scope

- In scope: dry-run no mutation fixture, apply creates expected files fixture, and host/review/merge-ready/closeout/generated-skill truth negative fixture.
- Out of scope: new scaffold artifact types, #1149/#1150 negative validate fixtures, #1152 generated-skill parity, #1153 PR gate/merge-ready/closeout integration, parent FR closeout, or merge.

## Scenarios

### Scenario S1

Given
- an empty fixture target

When
- `loom suite scaffold --suite full --json` runs without `--apply`

Then
- the payload plans the contracted full suite scaffold artifacts, reports no created locators, and leaves the target tree unchanged.

### Scenario S2

Given
- an empty fixture target

When
- `loom suite scaffold --suite full --json --apply` runs

Then
- the command creates only `suite-index.md`, `spec.md`, `plan.md`, `research.md`, `contracts.md`, and `readiness-checklist.md` below `.loom/specs/<item>/`.

### Scenario S3

Given
- forbidden host, review, merge-ready, closeout, work item, progress, and generated skill truth surfaces exist in the fixture target

When
- `loom suite scaffold --suite full --json --apply` runs

Then
- those forbidden surfaces are unchanged and created locators remain limited to `.loom/specs/<item>/`.

## Acceptance Criteria

- A1: `tools/check_cli_contract.py` still covers scaffold dry-run/apply boundaries and forbidden truth surfaces.
- A2: `loom_check` source fixture runs scaffold dry-run/apply/host-truth-negative assertions.
- A3: `loom_check` installed pre-merge fixture runs the same scaffold mutation boundary assertions.
- A4: Runtime copies remain synchronized and no `/speckit.*` command or `.specify/` layout is introduced.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `require_scaffold_mutation_boundary_validation` dry-run snapshot assertion.
  - S2 -> `require_scaffold_mutation_boundary_validation` apply created-locator assertion.
  - S3 -> `require_scaffold_mutation_boundary_validation` forbidden truth snapshot assertion.
- Acceptance coverage:
  - A1 -> focused CLI contract check.
  - A2 -> source `loom_check` source-self fixture.
  - A3 -> installed pre-merge fixture path inside source-self fixture.
  - A4 -> skills surface and generated/runtime parity checks.
- Expected evidence locator: .loom/specs/WI-1151/evidence-map.md
- Freshness rule: evidence is fresh only after local contract/source checks pass on the current head.
