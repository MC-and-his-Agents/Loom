# WI-1032 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: not_applicable; this WI updates the suite entry contract itself and does not need a separate full suite index.
- Consumes:
  - Work Item / FR locator: #1032 / #1015
  - Story Readiness confirmed locator, blocking locator, or `not_applicable` rationale: #1029, #1030, #1031 define the upstream story readiness contract and scaffold boundary.
  - Story scenario locator, or `not_applicable` rationale: not_applicable; methodology/template contract change, not product behavior.
  - Story Business Confirmation confirmed locator, blocking locator, or `not_applicable` rationale: #1029, #1030, #1031 define the upstream business confirmation contract and scaffold boundary.
- Produces:
  - Scenario ids / locators: S1-S3 in this spec.
  - Acceptance ids / locators: A1-A5 in this spec.
  - Behavior evidence expectation: docs/template source diff plus focused rg and contract-only loom_check.
- Locator:
  - Spec locator: .loom/specs/WI-1032/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1032, #1015, #1029, #1030, #1031
  - Freshness rule: reread upstream issue/PR state before closeout.

## Goal

Formal spec shaping must consume Story Readiness and Story Business Confirmation as explicit entrance conditions instead of treating any story text as enough to continue.

## Scope

- In scope:
  - `docs/methodology/templates/spec-suite.md`
  - docs scaffold templates for `spec.md`, `plan.md`, and `full-suite-index.md`
  - WI-1032 local carrier/spec/plan records
- Out of scope:
  - Redefining story intake semantics
  - Implementing gate-chain runtime enforcement
  - Updating generated skills/runtime surfaces owned by #1020
  - Defining full/minimal suite expansion owned by #1016/#1033

## Key Scenarios

### Scenario S1

Given a User Story exists for a formal spec path

When an agent starts shaping `spec.md`

Then the spec suite entry rules require Story Readiness to be `confirmed` or explicitly `not_applicable` before consuming story semantics.

### Scenario S2

Given Story Readiness or Story Business Confirmation is `pending` or `revision-requested`

When an agent tries to continue into `spec.md` or `plan.md`

Then the status is recorded only as a blocking locator and the agent returns to story shaping or waits for confirmation.

### Scenario S3

Given story intake is not applicable to a governance, maintenance, formatting, or link-only item

When the spec suite consumes that absence

Then `not_applicable` must include rationale, consumer boundary, and recheck condition instead of being treated as a missing field.

## Behavior Evidence

- Story scenario mapping: not_applicable; this is a methodology/template contract change.
- Story readiness locator or `not_applicable` rationale: #1029/#1030/#1031 consumed as upstream completed contract work.
- Story business confirmation locator or `not_applicable` rationale: #1029/#1030/#1031 consumed as upstream completed contract work.
- Scenario coverage:
  - S1 -> `docs/methodology/templates/spec-suite.md`
  - S2 -> `docs/methodology/templates/spec-suite.md`, `docs/methodology/templates/scaffold/spec.md`, `docs/methodology/templates/scaffold/plan.md`
  - S3 -> `docs/methodology/templates/spec-suite.md`, `docs/methodology/templates/scaffold/full-suite-index.md`
- Expected evidence locator: PR checks and #1032 completion comment.
- Freshness rule: validation must run on the PR head after final push.
- Execution ledger acceptance locator: .loom/specs/WI-1032/spec.md
- `not_applicable` rationale, if this is not a behavior-bearing change: observable behavior is downstream agent/template consumption, validated structurally.

## Acceptance Criteria

- [ ] A1: Spec suite entrance rules mention Story Readiness separately from Business Confirmation.
- [ ] A2: `pending` and `revision-requested` are blocking states for formal spec shaping.
- [ ] A3: `not_applicable` requires rationale, consumer boundary, and recheck condition.
- [ ] A4: `spec.md` and `plan.md` consume locators/consumed state rather than copying User Story truth.
- [ ] A5: Completion evidence links #1032 back to #1015 and #1029-#1031.
