# Plan

## Implementation Goal

Add the WI-1024 delivery planning contract and bind it to Loom's repo-local fact chain without implementing downstream #1025-#1028 surfaces.

## Phases

### Phase 1

- Objective: Define the delivery planning contract.
- Deliverable: `docs/methodology/templates/delivery-planning.md`.
- Exit condition: The document covers input, output, applicability, non-goals, authority boundary, provenance, freshness, and consumer mapping.

### Phase 2

- Objective: Make the contract discoverable from the templates area.
- Deliverable: `docs/methodology/templates/README.md` index update.
- Exit condition: The templates README lists the delivery planning contract as a current template-layer rule.

### Phase 3

- Objective: Bind the implementation to WI-1024.
- Deliverable: WI-1024 work item, progress, spec, plan, implementation contract, status surface, and bootstrap current item locator updates.
- Exit condition: The fact chain points to WI-1024 for the current batch.

## Constraints

- Architectural or governance constraints: delivery planning is a planning layer, not an execution state or completed truth.
- Workspace / rollout constraints: branch `work/1024-delivery-planning-contract`, PR pending.
- Purity or scope constraints: no #1025 issue-tree-plan scaffold, no #1026 PR slicing strategy, no #1027 GitHub mapping, no #1028 skill routing, no CLI automation.

## Validation

- Automated checks: `git diff --check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Manual checks: `rg -n "delivery planning|Phase|FR|Work Item|PR plan|不替代" docs/methodology docs/adoption skills src .loom`.
- Runtime evidence: not_applicable.
- Behavior evidence: docs and issue comments show the contract is consumable.
- Story scenario to evidence mapping: not_applicable.
- Story business confirmation locator or `not_applicable` rationale: not_applicable; methodology contract clarification.
- Fresh verification evidence: PR head plus review records.
- Execution ledger plan locator: `.loom/specs/WI-1024/plan.md`.
- Execution ledger validation evidence locator: `.loom/progress/WI-1024.md`.

## Test Strategy

- TDD or test-first expectation: not_applicable for documentation-only methodology work.
- Regression coverage to add or preserve: source contract-only `loom_check` and targeted anchor search.
- Cases that are intentionally not automated: planning judgment for exact Phase / FR / Work Item counts, which is consumed by later issue-tree planning.
- How failing tests or equivalent checks will be introduced before implementation: not_applicable.
- How passing tests or equivalent checks will be captured as test evidence: `.loom/progress/WI-1024.md`, PR checks, and #1024 comment.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence: not_applicable.

## Dependencies

- Blocking inputs: #1014 FR boundary and #1013 SDD internalization boundary.
- Required coordination: #1025, #1026, #1027, and #1028 consume this contract after merge.
- Rollback boundary: revert this PR if delivery planning is judged to duplicate execution truth or conflict with Work Item authority.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
