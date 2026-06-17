# WI-1511 Plan

## Suite Contract

- Suite path consumed: minimal
- Consumes:
  - Spec locator: `.loom/specs/WI-1511/spec.md`
  - Acceptance scenarios: S1-S5 in `.loom/specs/WI-1511/spec.md`
  - Work Item: `.loom/work-items/WI-1511.md`
  - GitHub issue: https://github.com/MC-and-his-Agents/Loom/issues/1511
- Produces:
  - Runtime behavior in `src/skills/shared/scripts/loom_flow.py`
  - Synced runtime copies under `skills/shared`, `.loom/bin`, skill runtimes, and demo project
  - CLI contract coverage in `tools/check_cli_contract.py`
  - Fresh verification evidence in `.loom/progress/WI-1511.md`

## Implementation Goal

Deliver review/head binding evidence inside gate freeze and make it fail closed when authored review approval cannot be consumed for the current PR head.

Explicitly deferred:

- #1510 carrier refresh/shadow freshness binding.
- #1512 hosted admission snapshot consumption.
- #1513 milestone-wide failure classifier expansion.
- #1514 docs/skills/fixtures sweep beyond focused WI-1511 artifacts.
- #1515 release/no-release closeout.

## Phases

### Phase 1: Inventory and fixture design

- Objective: inspect current `gate-freeze`, review binding, PR gate, and CLI contract fixtures.
- Deliverable: precise edit points and expected payload shape.
- Exit condition: focused fixture cases for fresh, carrier-only, stale, and invalid review/disposition inputs are identified.

### Phase 2: Runtime implementation

- Objective: add `review_head_binding` freeze evidence without weakening authored review authority.
- Deliverable: runtime payload fields, result/next-action behavior, and synced runtime copies.
- Exit condition: local freeze command emits expected review binding results.

### Phase 3: Contract tests and carrier refresh

- Objective: capture behavior in CLI contract tests and update WI-1511 carriers.
- Deliverable: updated `tools/check_cli_contract.py`, suite artifacts, recovery/status validation summary.
- Exit condition: focused local validation passes.

## Constraints

- Keep ordinary implementation PR semantic review binding strict.
- Do not let terminal closeout retained-review logic satisfy ordinary current-head implementation review.
- Do not add GitHub live mutations or hosted workflow changes in this Work Item.
- Keep runtime sync mechanical and verify generated-tree drift.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1511 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1511 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1511 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1511 --json`
- PR metadata preflight/readback and hosted checks before merge.

## Test Strategy

- Add or update CLI contract fixtures for:
  - fresh review/head binding pass
  - allowed carrier-only drift pass
  - stale implementation drift block
  - missing/invalid review or semantic disposition block
- Use the contract tests as the inner loop and gate-freeze command output as behavior evidence.

- Acceptance mapping:
  - A1 -> behavior evidence: gate freeze output and `tools/check_cli_contract.py` assert machine-readable review/head binding evidence.
  - A2 -> test evidence: CLI contract fixture for fresh and allowed carrier-only bindings asserts changed and disallowed path fields.
  - A3 -> test evidence: CLI contract fixture for stale semantic drift and invalid review/disposition inputs asserts block result and next action.
  - A4 -> automated validation evidence: `python3 tools/check_cli_contract.py`, `python3 -m py_compile ...`, and `git diff --check`.
  - A5 -> structural check: `python3 tools/skills_surface.py check --surface generated-tree-drift`, plus suite evidence/carrier validation for WI-1511 carriers.

## Dependencies

- Hard dependencies: #1507 and #1508 are merged/closed.
- Related reference: #1285 authored review/head binding policy.
- Parallel but not blocking for implementation: #1510 and #1509 closeout sync.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness formal artifact is out of scope for this bounded harness hardening item; rationale: the change is a runtime/contract hardening slice under an existing accepted issue; consumer boundary: spec, plan, implementation contract, evidence map, task carrier, review, and PR gate; recheck condition: require story readiness if the scope expands into product/business workflow behavior.
- [x] Story business semantics formal artifact is out of scope; rationale: WI-1511 changes gate evidence classification and does not introduce user-facing business semantics; consumer boundary: CLI contract, suite validation, review, and merge-ready; recheck condition: require business semantic confirmation if the change affects adoption behavior, external visible operations, or downstream product semantics.
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations map to test evidence
- [x] Risks and dependencies are explicit
