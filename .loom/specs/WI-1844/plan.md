# Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1844 is a bounded release aftercare wrapper and docs update with focused CLI contract and dogfood dry-run evidence. consumer boundary: suite validate, review, PR gate, merge-ready, controlled merge, issue closeout, and release/no-release decision may consume this minimal plan plus focused validation evidence. recheck condition: require full suite artifacts if scope expands into publishing, republishing, GitHub Release/npm mutation, automatic merge, multi-repo orchestration, new carrier/DSL, or release policy changes.
- Consumes:
  - Spec locator: .loom/specs/WI-1844/spec.md
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: skip rationale: #1844 issue tree is the scoped product source; require story readiness if the command expands into a broader release workflow or external host mutation.
  - Story Business Confirmation consumed state: skip rationale: the issue tree already defines the product boundary and no separate business semantic carrier is needed; require business confirmation if release policy, package publication semantics, or downstream governance guarantees change.
- Produces:
  - Validation strategy by scenario: contract test plus dogfood dry-run.
  - Test strategy by acceptance: `release-readback` surface and aggregate CLI contract.
  - Fresh verification evidence expectation: recorded in .loom/progress/WI-1844.md.
- Locator:
  - Plan locator: .loom/specs/WI-1844/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: #1844, #1842, #1843, #1846.
  - Freshness rule: rerun targeted checks after implementation or docs changes.

## Implementation Goal

Deliver the smallest wrapper that composes existing release readback, release PR readback, carrier closeout-sync, recovery writeback, carrier refresh, and next-command guidance.

Deferred: live closeout PR body mutation before post-commit head exists; the command emits exact next commands instead.

## Phases

### Phase 1

- Objective: Add CLI contract and wrapper.
- Deliverable: `tools/loom.py` command matrix and `handle_release closeout-sync`.
- Exit condition: help matrix and targeted contract pass.

### Phase 2

- Objective: Add regression evidence and docs.
- Deliverable: `tools/check_cli_contract.py`, README, README.zh-CN, CLI matrix.
- Exit condition: aggregate CLI contract and dogfood dry-run pass.

## Constraints

- No new DSL, no new carrier, no Loom-repo-specific release logic.
- No host/npm/GitHub Release mutation.
- `--apply` can only write repo carrier/status/shadow surfaces.
- Preserve review, PR gate, head binding, CI rollup, release readback, and closeout evidence.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- Manual checks:
  - Dogfood dry-run: `python3 tools/loom.py release closeout-sync --target . --version v0.24.0 --commit 1aafb7fb031d997b7b497e277a525e308f766407 --item WI-1834 --pr 1840 --json --full-output`
- Runtime evidence: .loom/progress/WI-1844.md
- Behavior evidence: targeted contract and dogfood dry-run.
- Story scenario to evidence mapping:
  - S1 -> automated validation evidence: targeted release-readback contract and dogfood dry-run.
  - S2 -> automated validation evidence: targeted release-readback contract drift blocker fixture.

## Test Strategy

- TDD or test-first expectation: add a focused contract test around the wrapper.
- Regression coverage to add or preserve: dry-run non-mutation, apply delegation sequence, release drift fail-closed, closeout/merge_ready shadow refresh.
- Cases that are intentionally not automated: live GitHub/npm publish; covered by dry-run readback and later release checks.
- Acceptance test mapping:
  - A1 -> test evidence: help matrix contract.
  - A2 -> test evidence: release-readback contract.
  - A3 -> test evidence: release-readback contract.
  - A4 -> test evidence: release-readback contract.
  - A5 -> structural check: docs diff and CLI matrix.

## Subagent Output Integration

- Owned outputs: none; implementation was small enough for the main controller.
- Integration owner: main controller.
- Required evidence from each subagent: skip rationale: no implementation lane was delegated before the review lane because the code change was small and shared-carrier ownership stayed in the main controller; require lane evidence if another agent writes code, docs, tests, PR metadata, or shared carrier surfaces.
- Review or reconciliation needed before merge-ready: semantic review and PR gate after PR metadata binds current head.
- Handoff notes locator, or skip rationale: skip rationale: the current Codex thread and repo carriers contain the active handoff state; author a handoff note if this work is paused, delegated, or transferred before PR gate.

## Dependencies

- Blocking inputs: #1842 contract before #1843 implementation; #1846 verification before #1845 release.
- Required coordination: GitHub/npm release permission only for #1845.
- Rollback boundary: revert one PR; no external release mutation in implementation PR.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly covered by skip rationale
- [x] Story business semantics are confirmed or explicitly covered by skip rationale
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or documented skip rationale
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has authored rationale, consumer boundary, and recheck condition
- [x] Risks and dependencies are explicit
