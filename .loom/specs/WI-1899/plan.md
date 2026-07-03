# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1899 is a bounded runtime path resolver implementation slice with focused behavior fixtures and no new product workflow, user-facing adoption flow, external host mutation, legacy migration apply, or release behavior; consumer boundary: suite validate, review, PR gate, merge-ready, #1900/#1901/#1908 follow-up planning, and closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if the work expands into repo carrier slimdown, full gate independence validation, workstation upgrade orchestration, legacy migration apply, permissions, or release behavior.
- Consumes:
  - Spec locator: .loom/specs/WI-1899/spec.md
  - Scenario ids / locators: S1-S4 in .loom/specs/WI-1899/spec.md#key-scenarios
  - Acceptance ids / locators: A1-A6 in .loom/specs/WI-1899/spec.md#acceptance-criteria
  - Story Readiness consumed state: not required; #1899 issue is the scoped readiness carrier.
  - Story Business Confirmation consumed state: not required; internal operating-layer behavior.
- Produces:
  - Runtime path helper implementation.
  - Consumer updates for runtime artifacts, tmp artifacts, PR metadata, gate freeze, review runtime, execution attempt history, and CLI agent-safe output artifacts.
  - Focused regression fixtures for resolver, PR metadata, runtime-upgrade, PR gate readback, and closeout.
- Locator:
  - Plan locator: .loom/specs/WI-1899/plan.md
- Provenance:
  - Source issue / PR / doc locator: issue #1899; issue #1898 repo/global artifact classification contract.
  - Freshness rule: Recheck after path resolver, emitted locators, or focused fixtures change.

## Implementation Goal

Default runtime/tmp output writes to workstation global cache while preserving the existing logical locator contract and legacy read compatibility.

## Phases

### Phase 1

- Objective: Add global runtime cache path helpers.
- Deliverable: `runtime_paths.py` helpers for workstation root, repo id, global cache root, runtime/tmp locator detection, physical path mapping, and physical-to-logical locator round trip.
- Exit condition: `runtime-paths` fixture proves global mapping and repo truth exclusion.

### Phase 2

- Objective: Route `loom_flow.py` runtime artifact consumers through the helper.
- Deliverable: write/read helpers for runtime artifacts, global review runtime roots, execution attempt persistence/read fallback, PR metadata artifacts, gate freeze artifacts, and logical evidence locators.
- Exit condition: PR metadata, PR gate target/readback, and governance closeout surfaces pass.

### Phase 3

- Objective: Route CLI agent-safe `.loom/tmp` output artifacts through global cache.
- Deliverable: `tools/loom.py` writes default output artifacts to global cache while returning `.loom/tmp/output-artifacts/...` locators.
- Exit condition: governance closeout surface reads agent-safe full-output artifacts from global cache.

### Phase 4

- Objective: Keep generated payloads synchronized.
- Deliverable: source, src mirror, plugin payload, repo-local `.loom/bin`, and example `.loom/bin` runtime copies updated.
- Exit condition: py_compile covers every touched copy.

## Constraints

- Do not move repository truth carriers.
- Do not implement repo carrier slimdown or migration apply.
- Do not change the user-facing CLI locator shape for `.loom/runtime/**` or `.loom/tmp/**`.
- Do not require global cache to satisfy truth when repo or host evidence is missing.

## Validation

- Automated checks:
  - `python3 -m py_compile tools/loom.py tools/check_cli_contract.py tools/loom_flow.py skills/shared/scripts/runtime_paths.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/runtime_paths.py src/skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/runtime_paths.py plugins/loom/skills/shared/scripts/loom_flow.py .loom/bin/runtime_paths.py .loom/bin/loom_flow.py examples/new-project/.loom/bin/runtime_paths.py examples/new-project/.loom/bin/loom_flow.py`
  - `python3 tools/check_cli_contract.py --surface runtime-paths --surface pr-metadata --surface runtime-upgrade --surface pr-gate-target-readback`
  - `python3 tools/check_cli_contract.py --surface governance-closeout`
  - `git diff --check`
- Manual checks:
  - Review diff to confirm no repo truth carrier resolver was changed to global-only.
- Runtime evidence:
  - Contract fixtures assert global runtime writes and repo-local absence.
- Behavior evidence:
  - `.loom/specs/WI-1899/evidence-map.md`
- Scenario validation mapping:
  - S1 -> automated test evidence EV-001, EV-002, EV-003, and EV-004.
  - S2 -> automated test evidence EV-001 and EV-005.
  - S3 -> automated test evidence EV-001.
  - S4 -> automated test evidence EV-005.
- Fresh verification evidence: .loom/progress/WI-1899.md validation summary.
- Execution ledger plan locator: .loom/specs/WI-1899/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1899/evidence-map.md

## Test Strategy

- Add a dedicated `runtime-paths` surface for direct resolver behavior.
- Update PR metadata and PR intent fixtures to assert global runtime artifact placement.
- Preserve closeout/gate fixtures that consume legacy repo-local execution attempts through read fallback.
- Cover `.loom/tmp` agent-safe output via governance closeout full-output artifact readback.
- Acceptance test mapping:
  - A1 -> test evidence EV-001.
  - A2 -> test evidence EV-001 and EV-005.
  - A3 -> test evidence EV-001 and static evidence EV-006.
  - A4 -> test evidence EV-002, EV-003, and EV-004.
  - A5 -> test evidence EV-004 and EV-005.
  - A6 -> test evidence EV-006 and synchronized runtime copies.

## Dependencies

- Blocking inputs: #1898 closed.
- Required coordination: #1900 consumes the logical/global locator split for repo carrier slimdown; #1908 consumes repo-local read fallback for migration.
- Rollback boundary: revert WI-1899 resolver and fixture changes only.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] Scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
