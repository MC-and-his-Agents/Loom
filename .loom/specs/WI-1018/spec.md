# WI-1018 Spec

## Goal

Define Loom-owned `evidence-map` and `consistency-analysis` contracts for #1018 so #1019 can consume stable evidence and consistency outputs without redefining them.

## Scope

- In scope:
  - `evidence-map` contract and scaffold.
  - `consistency-analysis` input, output, classification, freshness, and remediation contract.
  - Blocking consistency gap classification.
  - Status surface display boundary for derived evidence / consistency conclusions.
  - #1016 suite inputs consumed by locator only, and #1017 unstable inputs marked candidate / optional / deferred / not_applicable.
- Out of scope:
  - Full suite artifact list.
  - Task carrier truth.
  - Gate-chain implementation.
  - Skills routing.
  - Generated skills runtime surface.
  - CLI command surface.

## Key Scenarios

### Scenario 1

Given a Work Item has `spec.md`, `plan.md`, evidence locators, and host binding signals

When a later review or merge-ready consumer reads #1018 outputs

Then it can identify behavior evidence, test evidence, fresh verification evidence, source locator, freshness, and HEAD / PR / host state bindings without treating the map as evidence truth.

### Scenario 2

Given #1016 suite contracts are stable in `spec-suite.md` and #1017 task carrier contracts are not yet stable

When `evidence-map` or `consistency-analysis` references their inputs

Then #1016 inputs are consumed only by locator and applicability status, while #1017 inputs are represented only as candidate, optional, deferred, or not_applicable and do not redefine #1016 or #1017.

### Scenario 3

Given consistency analysis finds missing scenario mapping, stale evidence, host state conflict, or deferred-as-completed

When #1019 consumes #1018 outputs

Then it can distinguish blocking from advisory findings and route remediation without #1018 implementing gate-chain behavior.

## Behavior Evidence

- Story scenario mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; methodology contract work, no product story semantics.
- Scenario coverage: `docs/methodology/templates/evidence-map.md`; `docs/methodology/templates/consistency-analysis.md`; `docs/methodology/harness/status-surface.md`.
- Expected evidence locator: PR #1088 and #1018/#1041-#1044 completion comments.
- Freshness rule: stale if #1016 suite locators, future #1017 stable outputs, current HEAD, PR head, or host state contradict the locator / candidate / optional / deferred / not_applicable boundaries recorded here.
- Execution ledger acceptance locator: `.loom/specs/WI-1018/spec.md`.
- `not_applicable` rationale, if this is not a behavior-bearing change: contract-only methodology work; observable behavior is downstream review / merge-ready / closeout consumption.

## Exceptions And Boundaries

- Failure modes:
  - Treating evidence-map as evidence truth.
  - Treating locator-only #1016 inputs or candidate #1017 inputs as independently authored required truth.
  - Implementing #1019 gate-chain inside #1018.
  - Modifying skills routing or generated runtime surface before #1020.
- Operational boundaries:
  - Docs source surface only.
  - WI-1028 carrier terminalization is limited to stale active binding cleanup.
- Rollback or fallback expectations:
  - Revert #1018 contract docs if PR review finds boundary drift.

## Acceptance Criteria

- [x] Evidence-map binds Work Item, scope, HEAD, PR / host state, source locator, freshness, and not_applicable rationale.
- [x] Consistency-analysis distinguishes blocking / advisory / stale / missing / conflict / not_applicable.
- [x] Blocking consistency gap classification covers missing scenario mapping, stale evidence, host state conflict, and deferred-as-completed.
- [x] Status surface display remains derived and does not authored second truth.
- [x] #1020 integration remains deferred.
