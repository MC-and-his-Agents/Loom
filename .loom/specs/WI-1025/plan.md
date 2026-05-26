# WI-1025 Plan

## Implementation Goal

Deliver the issue-tree-plan methodology contract and scaffold template for #1025 without implementing downstream PR slicing, GitHub mapping, skills routing, task carrier, gate-chain, or CLI behavior.

## Phases

### Phase 1

- Objective: Define the issue-tree-plan contract.
- Deliverable: `docs/methodology/templates/issue-tree-plan.md`.
- Exit condition: Contract covers inputs, outputs, authority boundary, deferred/not_applicable, host carrier mapping, freshness, and consumers.

### Phase 2

- Objective: Add a directly usable scaffold.
- Deliverable: `docs/methodology/templates/scaffold/issue-tree-plan.md`.
- Exit condition: Scaffold exposes fillable fields for phase boundary, FR list, Work Item list, dependencies, deferred/not_applicable, host carrier mapping, and PR slicing placeholder.

### Phase 3

- Objective: Register the template and bind repo-local carriers.
- Deliverable: templates README plus WI-1025 fact chain, spec, plan, implementation contract, and review records.
- Exit condition: Local validation and PR checks consume WI-1025 as the current Work Item.

## Constraints

- Architectural or governance constraints: issue-tree plan is a planning artifact, not execution truth.
- Workspace / rollout constraints: branch `work/1025-issue-tree-plan-template`, PR pending.
- Purity or scope constraints: do not edit PR slicing, GitHub mapping, skills routing, task carrier, gate-chain, or CLI behavior.

## Validation

- Automated checks: `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Manual checks: `git diff --check`; focused `rg` checks from #1025.
- Runtime evidence: `.loom/progress/WI-1025.md`; `.loom/reviews/WI-1025.spec.json`; `.loom/reviews/WI-1025.json`.
- Behavior evidence: methodology contract and scaffold contain the required fields and forbidden-use statements.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Fresh verification evidence: local validation and PR checks before merge.
- Execution ledger plan locator: `.loom/specs/WI-1025/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1025.md`.

## Test Strategy

- TDD or test-first expectation: documentation/template-only change; use contract checks and focused grep.
- Regression coverage to add or preserve: preserve source contract checks.
- Cases that are intentionally not automated: qualitative planning judgment for actual Phase / FR / Work Item counts.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable; no executable behavior changes.
- How passing tests or equivalent checks will be captured as test evidence: validation commands and review records.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Subagent Output Integration

- Owned outputs: GitHub-only FR progress update may be delegated; repo files are owned by main agent.
- Integration owner: main agent.
- Required evidence from each subagent: issue comment URL and Project status if delegated.
- Review or reconciliation needed before merge-ready: verify GitHub issue #1025 and PR bindings.
- Handoff notes locator, or `not_applicable`: not_applicable.

## Dependencies

- Blocking inputs: #1024 delivery planning contract.
- Required coordination: #1026 consumes PR slicing placeholder; #1027 consumes host carrier mapping; #1028 consumes routing expectation.
- Rollback boundary: revert this PR if issue-tree plan duplicates execution truth or conflicts with delivery planning boundaries.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
