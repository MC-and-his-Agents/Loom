# Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1152 / #1145
- Story Readiness source: GitHub Work Item body is the scoped carrier.
- Story Business Confirmation source: governance regression only; business semantics are not required.
- Full suite artifacts not_applicable: rationale: #1152 is a narrow generated skills surface parity fixture Work Item; consumer boundary: suite validate, CLI contract checks, skills surface checks, and source/installed loom_check fixtures do not require full-path planning artifacts for this parity fixture; recheck condition: broaden to full suite if #1152 starts owning PR gate, merge-ready, closeout, or parent reconciliation behavior.

## Goal

Prove source and generated skills surfaces do not drift after suite integration.

## Scope

In scope:

- Route matrix parity between `src/skills`, generated `skills`, and per-skill `.loom-runtime`.
- Shared reference parity for spec suite, evidence map, consistency analysis, and task carrier references.
- Installed layout parity for `install-layout.json`, registry, and generated runtime package surfaces.
- CLI contract and source/installed `loom_check` coverage that consumes the parity fixture.

Out of scope:

- Unrelated skills content rewrites.
- #1150 stale host conflict fixtures.
- #1151 scaffold mutation fixtures.
- #1153 PR gate, merge-ready, or closeout integration fixtures.
- Project, #1145, or #1107 reconciliation and closeout.

## Scenarios

### Scenario S1

Given the source skills surface contains route matrix, install layout, registry, and shared references
When generated skills parity validation runs
Then the generated root `skills/` surface matches `src/skills/` for those stable parity files.

### Scenario S2

Given every generated skill package carries a `.loom-runtime` copy
When generated skills parity validation runs
Then each package runtime keeps route matrix, install layout, and registry parity with `src/skills`.

### Scenario S3

Given the full spec suite integration chain consumes generated skills checks
When CLI contract and source/installed `loom_check` validations run
Then the parity fixture is treated as evidence only and does not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.

## Acceptance Criteria

- A1: `tools/check_cli_contract.py` asserts `loom skills check --target . --json` consumes `tools/skills_surface.py check` and verifies stable source/generated/runtime parity locators.
- A2: `loom_check` source-self full-suite fixture consumes the generated skills parity validation.
- A3: `loom_check` installed pre-merge fixture consumes the same parity validation.
- A4: Source/generated/runtime copies remain synchronized and no `/speckit.*` command or `.specify/` layout is introduced.
