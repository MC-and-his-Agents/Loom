# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1900 is a bounded repo-carrier output contract slice that adds verifiable artifact metadata for existing agent-safe output and focused contract checks without adding a new user-facing workflow, external host mutation, migration apply, workstation upgrade orchestration, or release behavior; consumer boundary: suite validate, review, PR gate, merge-ready, #1901 follow-up planning, and closeout may consume this minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if the work expands into full gate independence validation, broad status/progress format redesign, workstation upgrade orchestration, legacy migration apply, permissions, or release behavior.
- Consumes:
  - Spec locator: .loom/specs/WI-1900/spec.md
  - Scenario ids / locators: S1-S3 in .loom/specs/WI-1900/spec.md#key-scenarios
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1900/spec.md#acceptance-criteria
  - Story Readiness consumed state: not required; #1900 issue is the scoped readiness carrier.
  - Story Business Confirmation consumed state: not required; internal operating-layer behavior.
- Produces:
  - Agent-safe output artifact metadata.
  - Contract helper hash verification for artifact-backed short envelopes.
  - Focused regression coverage for short envelope, global locator resolution, and hash mismatch rejection.
- Locator:
  - Plan locator: .loom/specs/WI-1900/plan.md
- Provenance:
  - Source spec / issue / doc locator: .loom/specs/WI-1900/spec.md; issue #1900; WI-1899 runtime/global locator contract.
  - Freshness rule: Recheck after `tools/loom.py`, `tools/check_cli_contract.py`, or runtime path resolver changes.

## Implementation Goal

Deliver a small, verifiable carrier-output contract:

- `tools/loom.py` exposes artifact SHA-256 metadata alongside the artifact locator for agent-safe output envelopes.
- Contract helpers resolve the logical locator, verify the artifact hash, and return the saved runtime payload.
- Focused contract coverage proves the short envelope stores only summary/locator/hash metadata while the full payload remains in the artifact.

Deferred: broad status/progress format redesign remains for later Work Items unless this implementation uncovers a direct regression.

## Phases

### Phase 1

- Objective: Freeze contract and carrier evidence.
- Deliverable: authored spec, plan, evidence map, task carrier.
- Exit condition: suite validators pass for WI-1900 scaffold.

### Phase 2

- Objective: Implement artifact metadata and validation.
- Deliverable: code change plus focused contract assertions.
- Exit condition: focused CLI contracts pass.

### Phase 3

- Objective: Review, PR, merge, and closeout.
- Deliverable: formal review record, PR metadata, merge-ready/closeout evidence.
- Exit condition: PR merged, issue #1900 closed, repo carrier terminalized.

## Constraints

- Repo truth must not depend on long inline logs.
- Logical `.loom/tmp/**` locators remain repo-relative even when resolved to global runtime storage.
- Hash verification must be over the saved artifact bytes, not over a reconstructed payload.
- Work only on branch `work/1900-carrier-artifact-locators`.
- Do not expand into workstation registry/orchestrator or legacy migration behavior.
- Preserve `--full-output` behavior.

## Validation

- Automated checks:
  - `python3 tools/check_cli_contract.py --surface governance-closeout`
  - `python3 tools/check_cli_contract.py --surface runtime-paths`
  - `python3 tools/loom.py suite validate --target . --item WI-1900 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1900 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1900 --json`
  - `git diff --check`
- Manual checks:
  - Review short envelope fixture output to confirm the full payload is not inlined.
  - Confirm artifact hash verifies against saved artifact bytes.
- Runtime evidence: contract command outputs bound in .loom/specs/WI-1900/evidence-map.md.
- Behavior evidence: S1-S3 covered by focused contract assertions.
- Scenario validation mapping:
  - S1 -> automated test evidence EV-001.
  - S2 -> automated test evidence EV-002.
  - S3 -> automated test evidence EV-001 and EV-003.
- Fresh verification evidence: .loom/progress/WI-1900.md validation summary.
- Execution ledger plan locator: .loom/specs/WI-1900/plan.md
- Execution ledger validation evidence locator: .loom/specs/WI-1900/evidence-map.md

## Test Strategy

- Add or update focused contract assertions before relying on implementation as complete.
- Cover agent-safe over-budget output writes an artifact and exposes locator/hash metadata.
- Cover contract helper rejection for missing or mismatched artifact metadata.
- Cover short envelope does not embed the complete payload.
- Acceptance test mapping:
  - A1 -> test evidence EV-001.
  - A2 -> test evidence EV-002.
  - A3 -> test evidence EV-001.
  - A4 -> test evidence EV-001 and manual envelope inspection.
  - A5 -> test evidence EV-003.

## Dependencies

- Blocking inputs: #1899 closed.
- Required coordination: #1901 consumes the artifact-backed carrier contract from #1900.
- Rollback boundary: revert WI-1900 output metadata and fixture changes only; do not change WI-1899 global runtime path resolver behavior.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] Scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
