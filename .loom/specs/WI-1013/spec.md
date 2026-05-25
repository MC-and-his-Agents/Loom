# Spec

## Goal

Define SDD as an internal Loom execution discipline so future work can use spec-kit lessons without copying spec-kit product surfaces or narrowing Loom into an SDD-only tool.

## Scope

- In scope:
  - `VISION.md` and `README.md` positioning.
  - `docs/methodology/templates/spec-suite.md` SDD boundary.
  - `docs/evidence/extraction-ledger.md` keep/adapt/drop evidence.
  - `docs/evidence/landing-map.md` landing and rejection boundaries.
- Out of scope:
  - Implementing full spec suite templates.
  - Defining delivery planning, story intake upgrades, task carrier, evidence-map, consistency-analysis, gate-chain changes, or CLI automation.

## Key Scenarios

### Scenario 1

Given Loom maintainers need to use spec-kit lessons

When they read the core positioning and spec-suite boundary

Then they can see that SDD is internalized as a formal spec execution discipline without replacing adoption, resume, review, merge-ready, closeout, repo companion, or host binding.

### Scenario 2

Given follow-up FRs #1014, #1015, and #1016 need to build on this boundary

When they consume the evidence ledger and landing map

Then they can cite keep/adapt/drop judgments without copying `.specify/`, `/speckit.*`, spec-kit fixed layout, or its extension trust model into Loom core.

## Behavior Evidence

- Story scenario mapping: not_applicable
- Story business confirmation locator or `not_applicable` rationale: governance boundary clarification, not a product story
- Scenario coverage: `VISION.md`; `README.md`; `docs/methodology/templates/spec-suite.md`; `docs/evidence/extraction-ledger.md`; `docs/evidence/landing-map.md`
- Expected evidence locator: PR #1054 and #1021/#1022/#1023 issue comments
- Freshness rule: evidence must bind to the PR head and current `WI-1013` review record
- Execution ledger acceptance locator: `.loom/specs/WI-1013/spec.md`
- `not_applicable` rationale, if this is not a behavior-bearing change: user-facing runtime behavior is not changed; governance/document behavior is observable through docs and issue dependency consumption

## Exceptions And Boundaries

- Do not create `docs/spec-kit/*`.
- Do not create `.specify/`.
- Do not claim full spec suite is already implemented.
- Do not close #1014, #1015, or #1016 from this work.

## Acceptance Criteria

- [x] Loom docs state SDD is internalized as an execution discipline, not an SDD-only product boundary.
- [x] Spec-kit absorption is recorded as keep / adapt / drop evidence.
- [x] Landing map provides paths for accepted and candidate items and rejects concrete spec-kit surfaces as archive-only.
- [x] Follow-up FRs can consume the boundary without re-deciding the positioning.
