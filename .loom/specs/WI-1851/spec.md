# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: #1851
  - Child locators: #1852, #1853, #1850, #1854
  - Story Readiness: N/A; rationale: this is a CLI governance usability improvement, not a product story; consumer boundary: spec shaping, review, merge-ready, and release closeout may consume this as story intake non-applicability only; recheck condition: scope introduces product workflow behavior, user-facing business semantics, or a new adoption story.
  - Story Business Confirmation: N/A; rationale: no business semantics are introduced; consumer boundary: spec shaping, review, merge-ready, and release closeout may consume this as business confirmation non-applicability only; recheck condition: scope changes product policy, customer-facing value proposition, pricing, security, data, or release governance semantics.
- Produces:
  - Scenario ids: S1, S2, S3, S4
  - Acceptance ids: A1, A2, A3, A4, A5
  - Behavior evidence expectation: CLI contract checks, skills checks, README/SKILL matrix review.
- Locator:
  - Spec locator: .loom/specs/WI-1851/spec.md
- Provenance:
  - Source issues: #1851/#1852/#1853/#1850/#1854
  - Freshness rule: revalidate after any CLI output, PR intent profile, generated skills, or docs matrix change.

## Goal

Reduce repeat rework from stale PR metadata, head binding, carrier, suite, and release closeout state by moving common checks into local command output before hosted gates.

## Scope

- In scope:
  - `loom-shift-left-readiness/v1` output on PR intent and release closeout paths.
  - PR intent prepare/check preserving existing valid `minimal` or `full` suite paths for closeout/carrier-sync Work Items.
  - PR intent prepare local metadata preflight after render.
  - Task-oriented help routes and command tiers.
  - README, README.zh-CN, CLI matrix, and skill route matrix alignment.
- Out of scope:
  - New gate scheduler.
  - Bulk repository upgrades.
  - Hosted gate replacement.
  - Large profile DSL or command renames.

## Key Scenarios

### Scenario S1

Given a closeout-only or carrier-sync-only PR for an existing Work Item with a valid minimal suite

When `loom pr-intent prepare/check` runs

Then Loom preserves the original suite path and does not force a formal-suite N/A decision.

### Scenario S2

Given a PR intent prepare path that renders metadata

When the command writes the body artifact under `--apply`

Then Loom immediately runs local metadata preflight and reports the next command before hosted gate.

### Scenario S3

Given a local check sees drift or an incomplete carrier set

When the command returns JSON

Then `readiness.ready_for_hosted_gate` is false, drift reasons are structured, and a single next command is present.

### Scenario S4

Given an operator needs a Loom command

When they run help or read the README/SKILL route matrix

Then the first view is task-oriented and the full command matrix remains available for advanced use.

## Minimal Path Applicability

- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: v0.25.0 shift-left readiness is a bounded CLI/docs contract change; consumer boundary: suite validate, review, merge-ready, and closeout require minimal suite evidence and do not require full path research/contracts/readiness artifacts; recheck condition: scope expands into a new scheduler, DSL, hosted gate replacement, security, data, or multi-repo orchestration behavior.

## Acceptance Criteria

- [ ] A1: PR intent closeout/carrier-sync profiles preserve valid existing suite paths.
- [ ] A2: PR intent prepare performs local metadata preflight after writing metadata artifacts.
- [ ] A3: Readiness output includes `ready_for_hosted_gate`, structured drift reasons, and one next command.
- [ ] A4: Help, README, README.zh-CN, CLI matrix, and SKILL route matrix expose the same task paths.
- [ ] A5: Contract checks and package/skills checks pass without lowering review, PR gate, hosted checks, release readback, or closeout evidence.
