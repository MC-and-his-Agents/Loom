# Spec

## Goal

Define a first-class delivery planning contract for Loom so later work can plan Phase / FR / Work Item / PR structure before implementation begins.

## Scope

- In scope:
  - Delivery planning methodology contract.
  - Input, output, applicability, non-goal, locator, provenance, freshness, and consumer boundaries.
  - Repo-local carriers for WI-1024.
- Out of scope:
  - Issue-tree-plan template (#1025).
  - PR slicing strategy (#1026).
  - GitHub Phase / FR / Work Item / Project mapping (#1027).
  - Skills routing (#1028).
  - Execution breakdown / task carrier, evidence-map, consistency-analysis, gate-chain, or CLI implementation.

## Key Scenarios

### Scenario 1

Given a Loom maintainer has a broad roadmap, story, product context, or governance goal

When they need to decide how many Phase, FR, Work Item, and PR units should exist

Then they can use delivery planning as the planning layer before any Work Item starts implementation.

### Scenario 2

Given a delivery planning result mentions GitHub Project, checklist, tasks.md, or an external tracker

When later agents consume the result

Then they can see that those host objects are organizational or task-carrier surfaces only and do not replace Work Item, review, merge-ready, or closeout truth.

### Scenario 3

Given #1025, #1026, #1027, and #1028 need stable upstream input

When they consume WI-1024

Then they can rely on explicit input/output, locator/provenance, freshness, and forbidden-use rules without redefining delivery planning.

## Behavior Evidence

- Story scenario mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: governance/methodology contract work, not product story semantics.
- Scenario coverage: `docs/methodology/templates/delivery-planning.md`; `docs/methodology/templates/README.md`.
- Expected evidence locator: PR pending and #1024 completion comment.
- Freshness rule: evidence must bind to the PR head and current WI-1024 review record.
- Execution ledger acceptance locator: `.loom/specs/WI-1024/spec.md`.
- `not_applicable` rationale, if this is not a behavior-bearing change: no runtime behavior changes; observable behavior is documentation and downstream issue consumption.

## Exceptions And Boundaries

- Do not create an issue-tree-plan scaffold in this Work Item.
- Do not define PR slicing rules beyond naming them as a downstream consumer.
- Do not implement GitHub automation or change Project structure.
- Do not claim #1014 or #1012 can close from this Work Item alone.

## Acceptance Criteria

- [x] Delivery planning contract defines inputs, outputs, applicability, and non-goals.
- [x] Contract says delivery planning does not replace Work Item, spec, plan, review, merge-ready, or closeout.
- [x] Contract defines locator, provenance, and freshness requirements.
- [x] Contract explains how #1025 issue-tree-plan, #1026 PR slicing, and #1027 GitHub mapping consume it.
- [x] WI-1024 carriers and validation evidence are current.
