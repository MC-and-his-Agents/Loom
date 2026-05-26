# WI-1027 Plan

## Implementation Goal

Deliver the GitHub host mapping contract for #1027 without implementing GitHub automation, skills routing, task carrier contracts, gate-chain behavior, or CLI commands.

## Phases

### Phase 1

- Objective: Extend the GitHub profile contract.
- Deliverable: `docs/adoption/github-profile.md`.
- Exit condition: Contract covers Phase, FR, Work Item, Project item, implementation PR, parent/sub-issue, blocked-by/blocks, Project Status semantics, authority boundaries, locator/provenance, and forbidden use.

### Phase 2

- Objective: Keep agent-facing reference surfaces synchronized.
- Deliverable: `skills/shared/references/adoption/github-profile.md` and `src/skills/shared/references/adoption/github-profile.md`.
- Exit condition: Reference copies match the source GitHub profile contract.

### Phase 3

- Objective: Bind repo-local carriers and review records.
- Deliverable: WI-1027 fact chain, spec, plan, implementation contract, and review records.
- Exit condition: Local validation and PR checks consume WI-1027 as the current Work Item.

## Constraints

- Architectural or governance constraints: GitHub host objects are carriers; Loom truth remains in Work Item, recovery, review, merge-ready, closeout, and controlled merge evidence.
- Workspace / rollout constraints: branch `work/1027-github-planning-mapping`.
- Purity or scope constraints: do not edit GitHub API automation, task carrier contracts, skills routing, gate-chain behavior, or CLI automation.

## Validation

- Automated checks: `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Manual checks: `git diff --check`; focused `rg` checks from #1027.
- Runtime evidence: `.loom/progress/WI-1027.md`; `.loom/reviews/WI-1027.spec.json`; `.loom/reviews/WI-1027.json`.
- Behavior evidence: GitHub profile contract contains required mapping fields and forbidden-use statements.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; no product story semantics are changed.
- Fresh verification evidence: local validation and PR checks before merge.
- Execution ledger plan locator: `.loom/specs/WI-1027/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1027.md`.

## Test Strategy

- TDD or test-first expectation: documentation/profile-only change; use contract checks and focused grep.
- Regression coverage to add or preserve: preserve source contract checks.
- Cases that are intentionally not automated: qualitative judgment for unusual host tracker mappings.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable; no executable behavior changes.
- How passing tests or equivalent checks will be captured as test evidence: validation commands and review records.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Subagent Output Integration

- Owned outputs: GitHub-only status/comment updates may be delegated; repo files are owned by main agent.
- Integration owner: main agent.
- Required evidence from each subagent: issue comment URL and Project status if delegated.
- Review or reconciliation needed before merge-ready: verify GitHub issue #1027 and PR bindings.
- Handoff notes locator, or `not_applicable`: not_applicable.

## Dependencies

- Blocking inputs: #1024 delivery planning contract, #1025 issue-tree-plan template, and #1026 PR slicing strategy.
- Required coordination: #1028 consumes GitHub mapping when updating skills routing; #1017 and #1020 can consume this host boundary later.
- Rollback boundary: revert this PR if GitHub Project, PR, checklist, or tasks.md semantics become authoritative over Work Item and closeout truth.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
