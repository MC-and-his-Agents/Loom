# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: .loom/specs/WI-1851/spec.md
  - Scenario ids: S1, S2, S3, S4
  - Acceptance ids: A1, A2, A3, A4, A5
  - Story Readiness consumed state: N/A; rationale: this plan consumes the spec's CLI-governance non-applicability decision; consumer boundary: validation planning, review, merge-ready, and release closeout may consume this as story intake non-applicability only; recheck condition: scope introduces product workflow behavior, user-facing business semantics, or a new adoption story.
  - Story Business Confirmation consumed state: N/A; rationale: this plan consumes the spec's no-business-semantics decision; consumer boundary: validation planning, review, merge-ready, and release closeout may consume this as business confirmation non-applicability only; recheck condition: scope changes product policy, customer-facing value proposition, pricing, security, data, or release governance semantics.
- Produces:
  - Validation strategy by scenario.
  - Contract tests for PR intent, readiness, release closeout, help route output, and generated skills parity.
  - Fresh verification evidence on the implementation PR head.
- Locator:
  - Plan locator: .loom/specs/WI-1851/plan.md
- Provenance:
  - Source issues: #1851/#1852/#1853/#1850/#1854
  - Freshness rule: rerun targeted checks after any CLI, docs, or generated skills payload change.

## Implementation Goal

Deliver the smallest local-readiness layer that prevents common drift from reaching hosted gates, without changing merge/release governance semantics.

## Out Of Scope Items

### Large Scheduler

- Locator: #1851 non-goals
- Rationale: local readiness should guide the next command, not schedule hosted gates.
- Recheck condition: repeated hosted gate races remain after local readback/preflight.
- Consumer boundary: implementation review, PR gate, and release closeout should not require a hosted gate scheduler for this item.

### Multi-repository Upgrade

- Locator: #1851 non-goals
- Rationale: v0.25.0 targets single-repo Loom command usability and drift prevention.
- Recheck condition: a future FR explicitly authorizes multi-repo runtime upgrade orchestration.
- Consumer boundary: runtime-upgrade docs and release evidence should not require multi-repository orchestration for this item.

### Full Suite Artifacts

- Locator: .loom/specs/WI-1851/spec.md#minimal-path-applicability
- Rationale: v0.25.0 is a bounded CLI/docs contract change with minimal automated contract coverage.
- Recheck condition: scope expands into a scheduler, DSL, hosted gate replacement, security, data, or multi-repo orchestration behavior.
- Consumer boundary: suite validate, review, merge-ready, and closeout for this Work Item should not require full suite artifacts.

## Phases

### Phase 1

- Objective: Define and emit local readiness.
- Deliverable: shared helper plus PR intent/release closeout output fields.
- Exit condition: contract tests see `loom-shift-left-readiness/v1`.

### Phase 2

- Objective: Preserve existing suite paths for closeout/carrier-sync profiles.
- Deliverable: effective profile suite resolution and regression test.
- Exit condition: closeout-only with a valid minimal suite passes without forcing a formal-suite N/A decision.

### Phase 3

- Objective: Align command discovery docs and skills.
- Deliverable: help task routes, README/README.zh-CN matrix, CLI matrix, generated skills route mirror.
- Exit condition: skills check and aggregate contract pass.

## Constraints

- Do not replace hosted gates with local readiness.
- Do not weaken review, PR gate, merge-ready, release readback, or closeout evidence.
- Do not force release/closeout Work Items with existing suites into a formal-suite N/A decision.
- Do not add a DSL, scheduler, or broad command rename.
- Generated skills and plugin payload hash must remain synchronized.

## Validation

- Automated checks:
  - `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
  - `python3 tools/check_cli_contract.py --surface pr-metadata`
  - `python3 tools/check_cli_contract.py --surface aggregate`
  - `python3 tools/loom.py skills check --target . --json`
  - `python3 tools/check_npm_package.py --surface plugin-payload-hash`
- Scenario validation mapping:
  - S1 -> automated validation strategy: aggregate PR intent fixture.
  - S2 -> automated validation strategy: aggregate PR intent prepare metadata preflight assertion.
  - S3 -> automated validation strategy: aggregate readiness assertions.
  - S4 -> automated validation strategy: help task route contract and skills generated-tree check.
- Fresh verification evidence: commands must run after final docs/skills/plugin hash changes on the implementation PR head.

## Test Strategy

- A1 -> test evidence: contract test in `assert_pr_intent_profile_fixture`.
- A2 -> test evidence: contract test in `assert_pr_intent_profile_fixture`.
- A3 -> test evidence: contract tests in PR intent and release closeout fixtures.
- A4 -> test evidence: `assert_governance_closeout_help_contract`, README review, skills generate/check.
- A5 -> test evidence: py_compile, aggregate CLI contract, skills check, plugin payload hash check.

## Subagent Output Integration

- Handoff notes locator: none; no subagent handoff is used for the current single-branch implementation.
- Required evidence from subagents: none; current implementation is single-branch and shared-carrier sensitive.

## Dependencies

- Blocking inputs: none after issue tree creation.
- Required coordination: release #1855 waits for #1852/#1853/#1850/#1854 implementation merge.
- Rollback boundary: revert the implementation PR; no external host state is mutated before PR/release steps.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A with rationale
- [x] Story business semantics are confirmed or explicitly N/A with rationale
- [x] Validation path is defined
- [x] BDD scenarios map to validation
- [x] TDD expectations map to contract checks
- [x] Risks and dependencies are explicit
