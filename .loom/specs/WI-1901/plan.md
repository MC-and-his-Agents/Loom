# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1901 is a focused runtime/cache contract check that extends an existing CLI contract surface without adding a new user workflow, migration apply path, host mutation, release behavior, or broad design surface; consumer boundary: suite validate, review, PR gate, merge-ready, and closeout may consume this minimal suite only as focused gate/cache regression proof; recheck condition: require full suite artifacts if scope expands into workstation upgrade orchestration, legacy migration apply, release behavior, permissions, hosted gate policy changes, or new public command semantics.
- Consumes:
  - Spec locator: .loom/specs/WI-1901/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1901/spec.md#key-scenarios
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1901/spec.md#acceptance-criteria
  - Story Readiness consumed state: not required; #1901 issue is the scoped readiness carrier.
  - Story Business Confirmation consumed state: not required; internal operating-layer behavior.
- Produces:
  - Focused cache-absent contract fixture inside `tools/check_cli_contract.py`.
  - Runtime-paths surface coverage for doctor/resume/review/pr-gate/merge-ready independence from repo-local cache.
- Locator:
  - Plan locator: .loom/specs/WI-1901/plan.md
- Provenance:
  - Source spec / issue / doc locator: .loom/specs/WI-1901/spec.md; issue #1901; issue #1900.
  - Freshness rule: Recheck after `tools/check_cli_contract.py`, `tools/loom.py`, runtime path resolver, or gate/read surface changes.

## Implementation Goal

Extend the existing `runtime-paths` contract check with one target repository fixture that proves cache-absent gate/read behavior:

- Build a metadata-only Loom fixture repo with stable carriers and installed-state.
- Remove repo-local `.loom/runtime` and `.loom/tmp`.
- Run doctor, resume, review read, PR gate, and merge-ready.
- Assert global runtime artifact resolution and no repo-local cache recreation.

## Phases

### Phase 1

- Objective: Add focused contract fixture.
- Deliverable: `assert_cache_absent_gate_contract` integrated into `run_runtime_paths_surface`.
- Exit condition: `python3 tools/check_cli_contract.py --surface runtime-paths` passes.

### Phase 2

- Objective: Freeze suite and carrier evidence.
- Deliverable: WI-1901 work item, progress, status, spec, plan, evidence map, and task carrier.
- Exit condition: suite validate/evidence/carrier pass.

### Phase 3

- Objective: Review, PR, merge, and closeout.
- Deliverable: formal review record, PR metadata, hosted checks, merge-ready, and closeout evidence.
- Exit condition: PR merged, issue #1901 closed, repo carrier terminalized.

## Constraints

- Work only on branch `work/1901-gate-no-repo-local-cache`.
- Do not refresh review/status/progress repeatedly while implementation is unstable.
- Do not move stable truth carriers to the global cache.
- Do not change public command semantics.
- Do not expand into workstation registry, workstation upgrade orchestrator, legacy migration, or release work.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/check_cli_contract.py`
  - `python3 tools/check_cli_contract.py --surface runtime-paths`
  - `python3 tools/loom.py suite validate --target . --item WI-1901 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1901 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1901 --json`
  - `git diff --check`
- Behavior evidence: S1-S3 covered by the focused `runtime-paths` contract fixture.
- Scenario validation mapping:
  - S1 -> automated test evidence EV-001 and EV-002.
  - S2 -> automated test evidence EV-002.
  - S3 -> automated test evidence EV-002.
- Acceptance test mapping:
  - A1 -> test evidence EV-002.
  - A2 -> test evidence EV-002.
  - A3 -> test evidence EV-002.
  - A4 -> test evidence EV-002.
  - A5 -> test evidence EV-002 and structural check EV-003.
- Fresh verification evidence: .loom/progress/WI-1901.md validation summary.
- Execution ledger plan locator: .loom/specs/WI-1901/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1901/evidence-map.md

## Dependencies

- Blocking inputs: #1900 closed.
- Required coordination: FR #1897 remains open until #1901 closes.
- Rollback boundary: revert WI-1901 contract fixture and carriers only; do not revert WI-1899/WI-1900 runtime cache behavior.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] Scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
