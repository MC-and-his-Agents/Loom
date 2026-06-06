# WI-1289-1291 Plan

## Suite Contract

- Suite path consumed: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: this plan covers a bounded runtime/gate repair with existing methodology contracts and no separate research or readiness workstream; consumer boundary: review, merge-ready, and closeout should consume this plan, evidence-map, task-carrier, review artifact, PR gate output, and hosted checks; recheck condition: require full-suite artifacts if scope expands beyond #1289/#1291 into a broader profile rollout, host API redesign, or multi-branch execution plan.
- Consumes:
  - Spec locator: `.loom/specs/WI-1289-1291/spec.md`
  - Scenario ids: S1, S2, S3
  - Acceptance ids: A1, A2, A3, A4, A5
- Produces:
  - Validation strategy by scenario: CLI contract fixtures plus local release/runtime parity checks
  - Test strategy by acceptance: targeted Python fixture assertions and generated runtime parity checks
  - Fresh verification evidence expectation: local validation commands and hosted checks for PR #1336
- Locator:
  - Plan locator: `.loom/specs/WI-1289-1291/plan.md`
- Provenance:
  - Source spec: `.loom/specs/WI-1289-1291/spec.md`
  - Source issues: #1289 and #1291
  - Freshness rule: re-run validation after any change to merge gate, PR gate, closeout diagnostics, generated runtime copies, PR metadata, or review record carriers

## Implementation Goal

Deliver the runtime changes for WI-1289 and WI-1291 in one PR:

- Extend `loom merge check/run` wrapper arguments so retained PR gate and host readback fixtures can be consumed.
- Make controlled merge consume `controlled_merge_consumption` before any `gh pr merge` delegation.
- Normalize PR merge timestamp fixture fields and add post-merge review diagnostics with repair plans.
- Add `authored_at` to newly written review records.
- Expose closeout and reconciliation findings for post-merge review bypass.
- Sync shared runtime copies across `skills/`, `src/skills/`, `.loom/bin`, and generated skill runtime payloads.
- Update the PR merge gate and review record methodology contracts.

## Phases

### Phase 1: Runtime Behavior

- Objective: Make merge check/run consume PR gate evidence and fail closed on drift.
- Deliverable: `tools/loom.py` wrapper arguments and `skills/shared/scripts/loom_flow.py` controlled merge consumption.
- Exit condition: controlled merge fixture passes with fresh PR gate evidence and blocks stale retained PR gate evidence.

### Phase 2: Post-Merge Diagnostics

- Objective: Diagnose post-merge review bypass without rewriting history.
- Deliverable: post-merge diagnostic payload, repair plan, closeout subcheck, reconciliation finding, and review `authored_at`.
- Exit condition: PR gate, closeout, and reconciliation fixtures expose blocking diagnostics and repair plan.

### Phase 3: Runtime Parity And Contracts

- Objective: Keep generated runtime and docs contracts aligned.
- Deliverable: generated skill runtime sync, `.loom/bin` sync, methodology docs, and package/release checks.
- Exit condition: skills surface, release surface, npm package, Python compile, and CLI contract checks pass.

## Constraints

- Do not weaken PR gate, review head binding, stale review semantics, or fail-closed merge behavior.
- Do not use raw host merge bypass as a completion path.
- Do not backdate review records or treat post-merge review evidence as pre-merge compliance.
- Keep the PR scoped to #1289 and #1291.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/loom_flow.py tools/check_cli_contract.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py`
  - `python3 tools/check_cli_contract.py`
  - `python3 tools/skills_surface.py check`
  - `python3 tools/check_release_surface.py`
  - `python3 tools/check_npm_package.py`
  - `git diff --check`
- Runtime evidence:
  - PR #1336 hosted checks
  - PR gate readback for head `f46825266096d5162f575b91d8be674e39fc6e1f`
  - Controlled merge readback before host merge
- Scenario validation mapping:
  - S1 -> `assert_semantic_review_disposition_pr_gate_fixture` controlled merge pass fixture
  - S2 -> retained PR gate head drift fixture in `tools/check_cli_contract.py`
  - S3 -> post-merge PR gate, closeout, and reconciliation fixture assertions
- Acceptance mapping:
  - A1 -> automated strategy: wrapper argument fixture coverage and PR body readback through `tools/check_cli_contract.py`.
  - A2 -> automated strategy: controlled merge consumption pass/block fixtures in `tools/check_cli_contract.py`.
  - A3 -> structural strategy: review record `authored_at` compile coverage plus review artifact readback.
  - A4 -> automated strategy: post-merge diagnostics and repair plan fixture coverage in PR gate, closeout, and reconciliation paths.
  - A5 -> structural strategy: `tools/skills_surface.py check`, release/package checks, runtime parity validation, and generated runtime copy hash checks.

## Dependencies

- Hard dependencies: #1287 and #1288 are closed/completed per scheduler readback.
- Required coordination: PR #1336 must pass hosted checks and merge through controlled merge.
- Rollback boundary: revert PR #1336; do not mutate historical review timestamps or host merge history.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Validation path is defined
- [x] Scenario and acceptance mapping is present
- [x] Risks and dependencies are explicit
