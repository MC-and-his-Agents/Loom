# WI-1909 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: existing workstation registry and global runtime cache contracts already define the authority boundary; this batch changes a bounded migration CLI surface and focused fixtures. consumer boundary: suite validate, review, PR gate, controlled merge, closeout, and FR-5 issue closeout may consume this minimal suite plus focused CLI contract validation. recheck condition: require full suite artifacts if scope expands into automatic multi-repo mutation, host-private Codex APIs, deleting host-owned tracked payloads, or release publishing.
- Consumes:
  - Spec locator: .loom/specs/WI-1909/spec.md.
  - Scenario ids / locators: S1-S5 in spec.
  - Acceptance ids / locators: A1-A7 in spec.
  - Story Readiness consumed state: n/a; FR/WI issue bodies define the batch.
  - Story Business Confirmation consumed state: n/a; no external business semantics.
- Produces:
  - Validation strategy by scenario: focused legacy migration CLI contract plus adjacent workstation registry checks.
  - Test strategy by acceptance: add `tools/check_cli_contract.py --surface legacy-migration`.
  - Fresh verification evidence expectation: local commands at final batch head and hosted PR gates.
- Locator:
  - Plan locator: .loom/specs/WI-1909/plan.md.
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1909/spec.md; issues #1909-#1913.
  - Freshness rule: stale after any legacy migration CLI, registry schema, global cache path, residue classification, or validation package boundary change.

## Implementation Goal

Deliver one FR-5 batch PR covering #1909, #1910, #1911, #1912, and #1913. This PR must not defer apply or validation package scope and must keep migration as an explicit opt-in maintenance action.

## Scope Retained Items

#1910 apply and #1913 validation package remain in scope for this batch. The work does not reduce release/milestone closeout scope owned by #1914.

## Omitted Full Suite Items

### Full Suite Artifacts

- Locator: suite-index.md, research.md, contracts.md, readiness-checklist.md.
- Rationale: existing workstation/global cache contracts already define the authority boundary; this batch changes a bounded migration CLI surface and fixtures.
- Recheck condition: scope expands into automatic multi-repo mutation, host-private Codex APIs, deleting host-owned tracked payloads, or release publishing.
- Consumers that should not require it: suite validate, review, PR gate, merge-ready, closeout for this bounded batch.

## Phases

### Phase 1

- Objective: Implement non-mutating planning for #1909/#1911/#1912.
- Deliverable: migration inventory, residue detection, ownership classification, strategy output, and fixture assertions.
- Exit condition: legacy migration surface covers S1/S3/S4/A1/A3/A4/A5.

### Phase 2

- Objective: Implement bounded apply for #1910.
- Deliverable: ignored cache move into global repo cache, workstation registry registration, and safe no-delete behavior for tracked payloads.
- Exit condition: legacy migration surface covers S2/A2 and proves tracked payloads are not auto-deleted.

### Phase 3

- Objective: Add post-migration validation package for #1913.
- Deliverable: installed-state validate, host verify, skills check, doctor, and git status validation summary in migration output.
- Exit condition: legacy migration surface covers S5/A6/A7.

### Phase 4

- Objective: Final batch verification and single carrier closeout.
- Deliverable: local validation, one review/shadow refresh, PR metadata, hosted checks, controlled merge, and closeout for #1909-#1913.
- Exit condition: all covered issues have closeout evidence after merge.

## Constraints

- `plan` must not mutate repository or workstation state.
- `apply` may move only ignored Loom cache/runtime paths and write global workstation cache/registry state.
- Do not delete tracked payloads automatically.
- Do not make migration a prerequisite for ordinary `doctor`, `status`, `resume`, or per-repo adoption validation.
- Do not refresh progress/status/review/shadow repeatedly while code is still moving; do final carrier refresh after implementation and validation stabilize.

## Validation

- Automated checks:
  - `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `git diff --check`
  - `python3 tools/check_cli_contract.py --surface legacy-migration`
  - `python3 tools/check_cli_contract.py --surface workstation-registry`
- Manual checks: inspect representative `loom migrate-global-cache plan --target <fixture> --json` and apply output for schema, strategy, moved artifact locators, and validation package.
- Runtime evidence: none before PR; hosted PR checks provide post-push evidence.
- Scenario validation mapping:
  - S1 -> automated test evidence: `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S2 -> automated test evidence: `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S3 -> automated test evidence: `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S4 -> automated test evidence: `python3 tools/check_cli_contract.py --surface legacy-migration`.
  - S5 -> automated test evidence: `python3 tools/check_cli_contract.py --surface legacy-migration`.
- Fresh verification evidence: final command outputs in PR body/review record.
- Execution ledger plan locator: .loom/specs/WI-1909/plan.md.

## Test Strategy

- TDD expectation: add legacy migration contract assertions before broad validation.
- Regression coverage to add or preserve:
  - Plan-only output remains non-mutating.
  - Apply moves only ignored cache/runtime paths into the global repo cache.
  - Tracked legacy residue is classified and never auto-deleted.
  - Strategy output covers no-op, auto-commit candidate, PR required, and blocked.
  - Validation package exposes installed-state, host verify, skills check, doctor, and git status outcomes.
- Cases intentionally not automated:
  - Real multi-repository migration; first version supports one explicit target.
  - Real Codex plugin marketplace update; FR-4 already reports plugin refresh guidance.
- Acceptance test mapping:
  - A1 -> test evidence: legacy-migration surface plan fixture assertions.
  - A2 -> test evidence: legacy-migration surface apply fixture assertions.
  - A3 -> test evidence: legacy-migration surface residue inventory assertions.
  - A4 -> test evidence: legacy-migration surface strategy classification assertions.
  - A5 -> test evidence: tracked residue remains in repository after apply.
  - A6 -> test evidence: validation package assertions.
  - A7 -> test evidence: adjacent workstation/adoption surfaces remain passing.

## Subagent Output Integration

- Owned outputs: none; no subagent implementation output is consumed for this batch so far.
- Integration owner: main thread.
- Required evidence from each subagent: none.
- Review or reconciliation needed before merge-ready: main thread review and final carrier refresh.
- Handoff notes locator, or n/a: n/a unless the thread is interrupted.

## Dependencies

- Blocking inputs: FR-2 and FR-3 are merged; FR-4 is closed and provides workstation upgrade baseline.
- Required coordination: PR body must list #1909, #1910, #1911, #1912, and #1913 as covered Work Items.
- Rollback boundary: one FR-5 batch PR over legacy migration CLI/tests/docs.

## Ready For Implementation

- [x] Spec is stable enough to implement.
- [x] Scope and non-goals are clear.
- [x] Story Readiness is confirmed or explicitly n/a.
- [x] Story business semantics are confirmed or explicitly n/a.
- [x] Validation path is defined.
- [x] BDD outer-loop scenarios map to validation.
- [x] TDD inner-loop expectations map to test evidence.
- [x] Every required scenario / acceptance mapping is present.
- [x] Risks and dependencies are explicit.
