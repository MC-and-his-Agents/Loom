# WI-1026 Plan

## Implementation Goal

Deliver the PR slicing methodology contract and scaffold template for #1026 without implementing downstream GitHub mapping, skills routing, task carrier, gate-chain, or CLI behavior.

## Phases

### Phase 1

- Objective: Define the PR slicing contract.
- Deliverable: `docs/methodology/templates/pr-slicing.md`.
- Exit condition: Contract covers inputs, output fields, same-PR conditions, split-PR conditions, primary/additional Work Item handling, review risk, validation matrix, merge-ready consumption, closeout consumption, and freshness.

### Phase 2

- Objective: Add a directly usable scaffold.
- Deliverable: `docs/methodology/templates/scaffold/pr-slicing.md`.
- Exit condition: Scaffold exposes fillable fields for candidate Work Items, dependency read, same-PR decision, PR body contract, review risk, validation matrix, merge-ready consumption, and closeout consumption.

### Phase 3

- Objective: Register the template and bind repo-local carriers.
- Deliverable: templates README plus WI-1026 fact chain, spec, plan, implementation contract, and review records.
- Exit condition: Local validation and PR checks consume WI-1026 as the current Work Item.

## Constraints

- Architectural or governance constraints: PR slicing is a planning/execution-boundary artifact, not execution truth.
- Workspace / rollout constraints: branch `work/1026-pr-slicing-strategy`, PR #1082.
- Purity or scope constraints: do not edit PR gate, merge-ready, GitHub mapping, skills routing, task carrier, or CLI behavior.

## Validation

- Automated checks: `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Manual checks: `git diff --check`; focused `rg` checks from #1026.
- Runtime evidence: `.loom/progress/WI-1026.md`; `.loom/reviews/WI-1026.spec.json`; `.loom/reviews/WI-1026.json`.
- Behavior evidence: methodology contract and scaffold contain required fields and forbidden-use statements.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Fresh verification evidence: local validation and PR checks before merge.
- Execution ledger plan locator: `.loom/specs/WI-1026/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1026.md`.

## Test Strategy

- TDD or test-first expectation: documentation/template-only change; use contract checks and focused grep.
- Regression coverage to add or preserve: preserve source contract checks.
- Cases that are intentionally not automated: qualitative judgment for actual PR grouping.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable; no executable behavior changes.
- How passing tests or equivalent checks will be captured as test evidence: validation commands and review records.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Subagent Output Integration

- Owned outputs: GitHub-only status/comment updates may be delegated; repo files are owned by main agent.
- Integration owner: main agent.
- Required evidence from each subagent: issue comment URL and Project status if delegated.
- Review or reconciliation needed before merge-ready: verify GitHub issue #1026 and PR bindings.
- Handoff notes locator, or `not_applicable`: not_applicable.

## Dependencies

- Blocking inputs: #1024 delivery planning contract and #1025 issue-tree-plan template.
- Required coordination: #1027 consumes PR slicing output when defining GitHub mapping; #1028 consumes routing expectation.
- Rollback boundary: revert this PR if PR slicing duplicates execution truth, weakens Work Item closeout, or conflicts with delivery planning/issue-tree-plan boundaries.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
