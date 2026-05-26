# WI-1016 Spec

## Goal

Define Loom full/minimal spec suite layering so #1017, #1018, and #1019 can consume a clear docs contract without redefining suite shape.

## Scope

- In scope: docs/methodology spec-suite contract, docs scaffold templates, spec.md to plan.md mapping, locator/provenance rules, not_applicable/deferred semantics, and #1020 generated handoff.
- Out of scope: task carrier, evidence-map, consistency-analysis, gate-chain, CLI, route matrix, scenario SKILL.md, and generated skills runtime surface.

## Key Scenarios

### Scenario S1

Given #1016 consumers need to choose a formal spec path

When they read the template methodology docs

Then minimal suite and full suite are both explicit legal paths with artifact lists and applicability rules.

### Scenario S2

Given a plan consumes a spec scenario or acceptance item

When the plan records validation and test strategy

Then each required scenario or acceptance item has a stable mapping or an explained not_applicable/deferred state.

### Scenario S3

Given generated skills integration is needed after docs contract changes

When #1016 records the requirement

Then the work is deferred to #1020 without modifying generated runtime surface in this PR.

## Behavior Evidence

- Story scenario mapping: not_applicable; this is a methodology/template contract.
- Story business confirmation locator or not_applicable rationale: not_applicable; no product story semantics are changed.
- Scenario coverage:
  - S1 -> docs/methodology/templates/spec-suite.md and docs/methodology/templates/scaffold/full-suite-index.md.
  - S2 -> docs/methodology/templates/spec-suite.md, docs/methodology/templates/scaffold/spec.md, and docs/methodology/templates/scaffold/plan.md.
  - S3 -> #1020 authoritative handoff comment and #1036 deferred handoff comment.
- Expected evidence locator: PR #1086 and #1033-#1036 comments.
- Freshness rule: evidence is current for PR #1086 head.
- Execution ledger acceptance locator: .loom/specs/WI-1016/spec.md.
- not_applicable rationale, if this is not a behavior-bearing change: behavior is documentation-consumption behavior.

## Exceptions And Boundaries

- Do not modify skills/route-matrix.md, src/skills/route-matrix.md, scenario SKILL.md, or generated skills runtime surface.
- Do not define #1017/#1018/#1019 owned contracts.
- Treat #1036 generated sync as deferred to #1020, not completed.

## Acceptance Criteria

- [x] A1: Minimal suite remains spec.md plus plan.md.
- [x] A2: Full suite has a docs artifact list and docs scaffold templates.
- [x] A3: Templates declare consume, produce, locator, and provenance.
- [x] A4: spec.md to plan.md mapping is mechanical enough for consumers.
- [x] A5: generated / skills integration is recorded for #1020 without runtime-surface changes.
