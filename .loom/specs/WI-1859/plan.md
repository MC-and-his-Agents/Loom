# Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: .loom/specs/WI-1859/spec.md
  - Scenario ids: S1, S2, S3, S4
  - Acceptance ids: A1, A2, A3, A4, A5
  - Story Readiness consumed state: N/A; rationale: this plan consumes the spec's CLI-governance non-applicability decision; consumer boundary: validation planning, review, merge-ready, and release closeout may consume this as story intake non-applicability only; recheck condition: scope introduces multi-repo orchestration, auto-merge, product issue auto-close, or new governance semantics.
  - Story Business Confirmation consumed state: N/A; rationale: this plan consumes the spec's no-business-semantics decision; consumer boundary: validation planning, review, merge-ready, and release closeout may consume this as business confirmation non-applicability only; recheck condition: scope changes user-facing product policy, security, data, release governance, or host authority behavior.
- Produces:
  - Validation strategy by scenario.
  - Contract tests for runtime-upgrade PR orchestration, closeout host readback, carrier sync sequencing, and help route output.
  - Fresh verification evidence on the implementation PR head.
- Locator:
  - Plan locator: .loom/specs/WI-1859/plan.md
- Provenance:
  - Source issues: #1859/#1860/#1861/#1862/#1863/#1864
  - Freshness rule: rerun targeted checks after any CLI, docs, generated skills, or plugin metadata change.

## Implementation Goal

Deliver the smallest safe runtime-upgrade lane that removes manual PR metadata, closedAt, merge commit, review-head, and carrier closeout stitching for a single repository.

## Out Of Scope Items

### Multi-repository Batch Mode

- Locator: #1859 non-goals
- Rationale: the current feedback is about repeated single-repository lane steps; batch coordination is project-specific.
- Recheck condition: a future FR explicitly authorizes multi-repo orchestration.
- Consumer boundary: implementation review, PR gate, docs, and release closeout should not require batch behavior.

### Automatic Merge Or Product Issue Closeout

- Locator: #1859 non-goals
- Rationale: runtime-upgrade may prepare safe next commands, but host merge and product issue closeout remain explicit human/governance actions.
- Recheck condition: a future FR defines a host-enforced auto-merge policy and closeout authority model.
- Consumer boundary: this item must not close product issues or merge PRs by default.

### Hosted Gate Scheduler

- Locator: #1859 non-goals
- Rationale: local readback and next-command guidance should reduce drift without owning hosted workflow orchestration.
- Recheck condition: repeated hosted gate races remain after PR metadata readback and closeout carrier guidance.
- Consumer boundary: implementation review and merge-ready should not require a new scheduler for this item.

## Phases

### Phase 1

- Objective: Add runtime-upgrade PR orchestration.
- Deliverable: `loom runtime-upgrade pr` render/create/update/readback path.
- Exit condition: runtime-upgrade contract test sees dry-run readiness false until PR readback and help exposes `pr`.

### Phase 2

- Objective: Add closeout host readback and carrier sync orchestration.
- Deliverable: issue readback, host-binding PR readback, terminal carrier sync, recovery writeback, closeout/merge-ready carrier refresh, closeout PR metadata next steps.
- Exit condition: contract test verifies issue `closedAt`, PR merge commit, target branch, hosted run URL, and `host-binding inspect -> carrier closeout-sync` sequence.

### Phase 3

- Objective: Align docs, generated skills, and package payload metadata.
- Deliverable: README/README.zh-CN/CLI matrix/route matrices plus refreshed plugin payload hash.
- Exit condition: runtime-upgrade and aggregate contract surfaces pass.

## Constraints

- Do not add multi-repository batch mode.
- Do not default to automatic merge or automatic product issue closeout.
- Do not weaken current-head review, PR metadata readback, hosted checks, PR gate, release readback, or closeout evidence.
- Do not treat CI or PR body metadata as semantic approval.
- Do not add a large policy DSL or gate scheduler.
- Generated skills and plugin payload hash must remain synchronized.

## Validation

- Automated checks:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
  - `python3 tools/check_cli_contract.py --surface runtime-upgrade`
  - `python3 tools/check_cli_contract.py --surface aggregate`
  - `python3 tools/check_npm_package.py --surface plugin-payload-hash`
- Scenario validation mapping:
  - S1 -> automated validation strategy: existing runtime-upgrade prepare fixture.
  - S2 -> automated validation strategy: new runtime-upgrade pr fixture.
  - S3 -> automated validation strategy: monkeypatched closeout host readback contract.
  - S4 -> automated validation strategy: closeout carrier-only review guidance and existing pr-gate carrier-only contract coverage.
- Fresh verification evidence: commands must run after final docs/skills/plugin hash changes on the implementation PR head.

## Test Strategy

- A1 -> test evidence: `run_runtime_upgrade_surface` PR dry-run/readiness assertions.
- A2 -> test evidence: `run_runtime_upgrade_surface` host readback closeout contract.
- A3 -> test evidence: `run_runtime_upgrade_surface` carrier closeout-sync delegation assertion.
- A4 -> test evidence: runtime-upgrade closeout payload `carrier_only_review` field and README/CLI matrix text.
- A5 -> test evidence: py_compile, runtime-upgrade surface, aggregate CLI contract, plugin payload hash.

## Dependencies

- Blocking inputs: none after issue tree creation.
- Required coordination: release #1865 waits for #1860/#1861/#1862/#1863/#1864 implementation merge/readback.
- Rollback boundary: revert the implementation PR; no external host state is mutated before explicit `--create`, `--update`, `--sync`, or release steps.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A with rationale
- [x] Story business semantics are confirmed or explicitly N/A with rationale
- [x] Validation path is defined
- [x] BDD scenarios map to validation
- [x] TDD expectations map to contract checks
- [x] Risks and dependencies are explicit
