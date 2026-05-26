# WI-1018 Plan

## Implementation Goal

Deliver #1018 contract documentation and scaffolds for evidence-map and consistency-analysis without changing skills routing, generated runtime surface, or gate-chain behavior.

## Phases

### Phase 1

- Objective: Define evidence-map contract and scaffold.
- Deliverable: `docs/methodology/templates/evidence-map.md`; `docs/methodology/templates/scaffold/evidence-map.md`.
- Exit condition: behavior evidence, test evidence, fresh verification evidence, source locator, binding, freshness, and not_applicable/deferred semantics are explicit.

### Phase 2

- Objective: Define consistency-analysis contract and blocking gap classification.
- Deliverable: `docs/methodology/templates/consistency-analysis.md`; `docs/methodology/templates/scaffold/consistency-analysis.md`.
- Exit condition: input snapshot, output envelope, classification, freshness, remediation direction, and blocking/advisory gap table are explicit.

### Phase 3

- Objective: Expose derived status surface display boundary and maintain carriers.
- Deliverable: `docs/methodology/harness/status-surface.md`; `.loom/*` WI-1018 carriers; terminalized `.loom/progress/WI-1028.md`.
- Exit condition: status surface reads derived evidence / consistency conclusions only, and this workspace has one active WI.

## Constraints

- Architectural or governance constraints:
  - Source docs are the authority for this PR.
  - #1016 suite inputs are consumed by locator only; #1017 unstable inputs stay candidate / optional / deferred / not_applicable.
  - #1019 consumes outputs later; #1018 does not implement gate-chain.
  - #1020 consumes skills / GitHub profile / generated surface later.
- Workspace / rollout constraints:
  - Work occurs on `work/1018-evidence-consistency-contract` in `/Users/mc/dev/Loom-1018-evidence-consistency-contract`.
- Purity or scope constraints:
  - No skills routing or generated runtime surface edits.

## Validation

- Automated checks:
  - `git diff --check`
  - focused `rg` checks for evidence-map / consistency-analysis / blocking / advisory / stale / missing / conflict / not_applicable / source locator / freshness / HEAD / host state / #1019 / #1020 boundaries
  - `python3 tools/skills_surface.py check`
  - `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Manual checks:
  - Confirm PR #1088 body and issue comments link #1018/#1041-#1044 evidence.
- Runtime evidence:
  - not_applicable.
- Behavior evidence:
  - Contract files and scaffolds are present and linked from templates README.
- Story scenario to evidence mapping:
  - not_applicable.
- Story business confirmation locator or `not_applicable` rationale:
  - not_applicable.
- Fresh verification evidence:
  - local validation summary in `.loom/progress/WI-1018.md`.
- Execution ledger plan locator:
  - `.loom/specs/WI-1018/plan.md`.
- Execution ledger validation evidence locator:
  - `.loom/progress/WI-1018.md`; `.loom/reviews/WI-1018.spec.json`; `.loom/reviews/WI-1018.json`; PR #1088.

## Test Strategy

- TDD or test-first expectation:
  - not_applicable for contract-only documentation; structural checks and Loom contract-only validation are the evidence path.
- Regression coverage to add or preserve:
  - Preserve `tools/skills_surface.py check` and source contract-only `loom_check` pass.
- Cases that are intentionally not automated:
  - Exact #1019 gate-chain consumption semantics and #1020 generated surface sync.
- How failing tests or equivalent checks will be introduced before implementation:
  - not_applicable; this PR validates by focused `rg` and existing source surface checks.
- How passing tests or equivalent checks will be captured as test evidence:
  - `.loom/progress/WI-1018.md` and PR #1088.
- How User Story acceptance scenarios map to tests, checks, manual validation, or `not_applicable` evidence:
  - not_applicable.

## Subagent Output Integration

- Owned outputs:
  - Read-only input boundary summaries for #1016/#1017 and status/review/merge-ready/closeout surfaces.
- Integration owner:
  - main agent.
- Required evidence from each subagent:
  - summarized findings with file / issue locators.
- Review or reconciliation needed before merge-ready:
  - WI-1018 spec review and implementation review records.
- Handoff notes locator, or `not_applicable`:
  - `.loom/progress/WI-1018.md`.

## Dependencies

- Blocking inputs:
  - #1018 issue body and current source docs.
- Required coordination:
  - #1016 suite truth remains owned by `spec-suite.md`; #1017 remains candidate / optional / deferred / not_applicable until stable.
  - #1019 and #1020 consume this PR after merge.
- Rollback boundary:
  - Revert PR #1088 contract docs and WI-1018 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story business semantics are confirmed or explicitly `not_applicable`
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or `not_applicable`
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
