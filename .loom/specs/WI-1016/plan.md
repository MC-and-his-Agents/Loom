# WI-1016 Plan

## Implementation Goal

- Deliver docs-only full/minimal spec suite contract and scaffold updates for #1016.
- Defer generated / skills surface sync to #1020.

## Phases

### Phase 1

- Objective: Define path layering and artifact responsibilities.
- Deliverable: docs/methodology/templates/spec-suite.md.
- Exit condition: minimal path, full path, artifact list, and not_applicable/deferred semantics are documented.

### Phase 2

- Objective: Add docs scaffold templates and strengthen spec/plan mapping.
- Deliverable: docs/methodology/templates/scaffold/*.md and README listing.
- Exit condition: scaffold templates declare consume, produce, locator, and provenance.

### Phase 3

- Objective: Record generated handoff and issue evidence.
- Deliverable: #1020/#1033-#1036 comments and PR #1086.
- Exit condition: generated sync is explicitly deferred and not implemented in this PR.

## Constraints

- Do not touch route matrix, scenario SKILL.md, or generated runtime surface.
- Do not define task carrier, evidence-map, consistency-analysis, gate-chain, or CLI contracts.
- Treat #1015/#1032 story readiness as an upstream locator rule only while those issues remain open.

## Validation

- Automated checks: git diff --check; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Manual checks: focused rg for full/minimal suite, mapping, locator/provenance, not_applicable/deferred.
- Runtime evidence: PR #1086 checks.
- Behavior evidence:
  - S1 -> docs/methodology/templates/spec-suite.md.
  - S2 -> docs/methodology/templates/scaffold/spec.md and docs/methodology/templates/scaffold/plan.md.
  - S3 -> #1020 and #1036 comments.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or not_applicable rationale: not_applicable.
- Fresh verification evidence: PR #1086 head and local validation commands.
- Execution ledger plan locator: .loom/specs/WI-1016/plan.md.
- Execution ledger validation evidence locator: .loom/progress/WI-1016.md.

## Test Strategy

- TDD or test-first expectation: not_applicable for docs-only methodology change.
- Regression coverage to add or preserve: source surface and contract-only loom_check must remain green.
- Cases intentionally not automated: semantic readability of the new docs contract, covered by issue comments and review.
- Passing tests or equivalent checks are captured in .loom/progress/WI-1016.md and PR checks.
- Acceptance test mapping:
  - A1 -> focused rg plus spec-suite doc inspection.
  - A2 -> scaffold file existence and README listing.
  - A3 -> focused rg for consume/produce/locator/provenance.
  - A4 -> focused rg for scenario/acceptance/validation/test strategy.
  - A5 -> #1020 handoff and no forbidden generated/runtime file changes.

## Dependencies

- Blocking inputs: #1013 closeout; #1016 issue body.
- Required coordination: #1020 consumes generated / skills handoff.
- Rollback boundary: revert PR #1086 docs and WI-1016 carrier changes.

## Ready For Implementation

- [x] Spec is stable enough to implement.
- [x] Scope and non-goals are clear.
- [x] Story business semantics are explicitly not_applicable.
- [x] Validation path is defined.
- [x] BDD outer-loop scenarios map to validation or not_applicable.
- [x] TDD inner-loop expectations map to test evidence or not_applicable.
- [x] Risks and dependencies are explicit.
