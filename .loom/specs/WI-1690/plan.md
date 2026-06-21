# WI-1690 Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1690`
- Consumes:
  - Spec locator: `.loom/specs/WI-1690/spec.md`
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Story Readiness consumed state: N/A
  - Story Business Confirmation consumed state: N/A
- Produces:
  - Validation strategy by scenario: focused root CLI wrapper contract tests.
  - Test strategy by acceptance: `ship-wrapper` surface plus aggregate command surface.
  - Fresh verification evidence expectation: `.loom/specs/WI-1690/evidence-map.md`
- Locator:
  - Plan locator: `.loom/specs/WI-1690/plan.md`
- Provenance:
  - Source spec / issue / PR / doc locator: issue #1690 and `.loom/specs/WI-1690/spec.md`
  - Freshness rule: Re-run focused checks after CLI wrapper, delegated args, closeout policy, or carrier changes.

## Implementation Goal

- Deliver a non-mutating `loom ship` dry-run wrapper that explains the intensity-aware delivery path.
- Keep apply-mode host/repo writes deferred to #1691.

## Deferred Items

- `loom ship --apply`
  - Locator: #1691
  - Reason: apply needs merge execution and closeout policy consumption after #1690 proves the dry-run contract.
  - Activation condition: dry-run path is merged and #1691 starts.
  - Does not currently block: #1690 dry-run validation.
  - Statement: deferred is not completed.

## Excluded Items

- `controlled-merge --closeout-run`: owned by #1692.
- milestone release: owned by #1696.
- closeout carrier batching: governed by #1695 and consumed by later apply/closeout work.

## Phases

### Phase 1

- Objective: Add the root CLI `ship` surface and dry-run handler.
- Deliverable: `tools/loom.py` can produce a `loom-ship/v1` plan without mutation.
- Exit condition: focused wrapper contract passes.

### Phase 2

- Objective: Add regression coverage for read-only delegation and fail-closed apply mode.
- Deliverable: `tools/check_cli_contract.py --surface ship-wrapper` covers dry-run sequence, closeout policy, skipped closeout, and `--apply` blocker.
- Exit condition: aggregate CLI contract still sees `ship` as an implemented command.

## Constraints

- Architectural or governance constraints: reuse existing root wrapper delegation and runtime payload helpers; do not add a new orchestration framework for #1690.
- Workspace / rollout constraints: work stays on branch `work/1690-ship-dry-run` in `/Users/mc/dev/Loom-WI-1690`.
- Purity or scope constraints: no GitHub writes, repo carrier writes from `ship` dry-run, issue closeout, merge execution, or release publishing.

## Validation

- Automated checks:
  - `git diff --check`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1690 --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1690`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1690`
  - `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1690 --build-evidence .loom/progress/WI-1690-build-evidence.json`
- Manual checks: inspect diff for scope containment and non-mutating delegated args.
- Runtime evidence: `ship-wrapper` contract invokes `handle_ship` with mocked delegated payloads.
- Behavior evidence: `tools/loom.py` `handle_ship`, `ship_closeout_policy`, and delegated dry-run sequence.
- Story scenario to evidence mapping: N/A; scenarios are in `spec.md`.
- Story readiness consumed: N/A.
- Story business confirmation locator or N/A rationale: N/A; no product-domain business semantics change.
- Scenario validation mapping:
  - S1 -> automated
  - S2 -> automated
  - S3 -> automated
- Fresh verification evidence: `.loom/specs/WI-1690/evidence-map.md`
- Execution ledger plan locator: `.loom/specs/WI-1690/plan.md`
- Execution ledger validation evidence locator: `.loom/specs/WI-1690/evidence-map.md`

## Test Strategy

- TDD or test-first expectation: add the wrapper contract regression while adding the dry-run handler.
- Regression coverage to add or preserve: command surface registration, dry-run delegation order, no mutating delegated flags, light closeout policy, and apply-mode fail-closed behavior.
- Cases that are intentionally not automated: live GitHub status variations are covered by delegated PR gate and merge check surfaces, not by this dry-run wrapper unit.
- How failing tests or equivalent checks will be introduced before implementation: the `ship-wrapper` contract fails until `handle_ship` exists.
- How passing tests or equivalent checks will be captured as test evidence: commands listed in Validation and evidence map rows.
- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
  - A5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
- A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
- A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
- A4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
- A5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`

## Subagent Output Integration

- Owned outputs: read-only implementation orientation from Archimedes subagent.
- Integration owner: main agent.
- Required evidence from each subagent: summary consumed into this plan and code review focus; no subagent-authored files.
- Review or reconciliation needed before merge-ready: standard spec review, implementation review, PR gate, merge-ready, and closeout.
- Handoff notes locator, or N/A: N/A.

## Dependencies

- Blocking inputs: #1682 and #1686 are complete; #1695 closeout policy is complete and consumed by policy decisions.
- Required coordination: #1691 consumes this dry-run surface for apply behavior; #1692 consumes the closeout-run boundary.
- Rollback boundary: revert `tools/loom.py`, `tools/check_cli_contract.py`, and WI-1690 carriers for this PR.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly N/A
- [x] Story business semantics are confirmed or explicitly N/A
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation or N/A
- [x] TDD inner-loop expectations map to test evidence
- [x] Every required scenario / acceptance mapping is present, or has N/A rationale and recheck condition
- [x] Risks and dependencies are explicit
