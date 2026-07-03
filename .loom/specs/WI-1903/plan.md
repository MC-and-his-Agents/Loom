# Plan

## Suite Contract

- Suite path consumed: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1903 is a bounded plan-only CLI slice over the already frozen workstation registry contract and does not implement apply, destructive migration, release, or host-visible writes; consumer boundary: suite validate, review, PR gate, merge-ready, and closeout may consume this minimal suite; recheck condition: require full suite artifacts if scope expands into `--apply`, cross-repo mutation, new registry schema semantics, security/permission behavior, or release mechanics.
- Consumes:
  - Spec locator: .loom/specs/WI-1903/spec.md
  - Scenario ids / locators: S1-S4 in .loom/specs/WI-1903/spec.md#key-scenarios
  - Acceptance ids / locators: A1-A5 in .loom/specs/WI-1903/spec.md#acceptance-criteria
- Produces:
  - Plan-only workstation upgrade command.
  - Focused workstation registry fixture coverage.
  - Runtime fixture/hash sync needed by source validation.
- Locator:
  - Plan locator: .loom/specs/WI-1903/plan.md
- Provenance:
  - Source spec / issue / doc locator: .loom/specs/WI-1903/spec.md; issue #1903; docs/adoption/workstation-registry-contract.md.
  - Freshness rule: Recheck after `tools/loom.py`, workstation registry fixtures, or `loom_check.py` runtime copies change.

## Implementation Phases

### Phase 1

- Objective: Add the plan-only workstation CLI surface.
- Deliverable: `tools/loom.py` parser, output schema, machine plan, and repo classification payloads.
- Exit condition: plan command is non-mutating and returns valid JSON for empty and populated registries.

### Phase 2

- Objective: Add focused regression coverage.
- Deliverable: workstation registry fixture checks for `machine_only`, `repo_noop`, `repo_auto_commit_candidate`, `repo_pr_required`, and `blocked`.
- Exit condition: `python3 tools/check_cli_contract.py --surface workstation-registry` passes.

### Phase 3

- Objective: Repair validation drift and freeze evidence.
- Deliverable: `loom_check.py` execution-attempt fixture reads the actual runtime locator, synchronized runtime copies, refreshed bootstrap hashes, and WI-1903 carriers.
- Exit condition: contract-only, generated-tree-drift, daily CLI fast, py_compile, and diff check pass.

## Validation

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/loom_check.py .loom/bin/loom_check.py examples/new-project/.loom/bin/loom_check.py`
- `git diff --check`
- `python3 tools/check_cli_contract.py --surface workstation-registry`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/loom_check.py --profile source --source-surface daily-execution-cli-fast .`

Scenario validation mapping:

- S1 -> automated test evidence EV-002.
- S2 -> automated test evidence EV-002.
- S3 -> automated test evidence EV-002.
- S4 -> automated test evidence EV-002.

Acceptance test mapping:

- A1 -> test evidence EV-002 and structural evidence EV-001.
- A2 -> test evidence EV-002.
- A3 -> test evidence EV-002.
- A4 -> test evidence EV-002.
- A5 -> test evidence EV-003, EV-004, EV-005, and EV-006.

## Constraints

- Do not write `~/.loom/repositories.json` from `upgrade --plan`.
- Do not write any target repository from `upgrade --plan`.
- Do not implement `--apply`.
- Do not fold #1904, #1905, #1906, #1907, or FR-5 legacy migration into this PR.
- Keep repository truth and workstation registry truth separate.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is confirmed or explicitly not required
- [x] Story business semantics are confirmed or explicitly not required
- [x] Validation path is defined
- [x] Scenario / acceptance mapping is present
- [x] Risks and dependencies are explicit
