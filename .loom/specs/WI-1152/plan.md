# Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1152/spec.md
- Plan locator: .loom/specs/WI-1152/plan.md
- Story Readiness consumed state: #1152 issue body
- Story Business Confirmation consumed state: not required because this is governance regression behavior.
- Freshness rule: refresh .loom/progress/WI-1152.md after final validation and before PR handoff.

## Phases

### Phase 1

- Objective: Add CLI contract coverage for generated skills surface parity.
- Deliverable: `tools/check_cli_contract.py` asserts skills check output and stable source/generated/runtime parity files.
- Exit condition: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py` passes.

### Phase 2

- Objective: Add source/installed `loom_check` consumption of the parity fixture.
- Deliverable: shared `loom_check` validates generated skills parity after full suite happy path validation in source and installed paths.
- Exit condition: source surface contract checks pass.

### Phase 3

- Objective: Synchronize generated and runtime surfaces and record evidence.
- Deliverable: regenerated `skills/` surface plus repo-local runtime copies.
- Exit condition: `tools/skills_surface.py check`, focused rg, and required source checks pass.

## Validation

- Scenario mapping:
  - S1 -> automated validation evidence: CLI contract stable source/generated parity assertions.
  - S2 -> automated validation evidence: CLI contract per-skill `.loom-runtime` parity assertions.
  - S3 -> automated validation evidence: source/installed `loom_check` generated skills parity consumption.
- Acceptance mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`.
  - A2 -> test evidence: source-self fixture check through `loom_check`.
  - A3 -> test evidence: installed pre-merge fixture through `loom_check`.
  - A4 -> structural evidence: `tools/skills_surface.py check` and focused `rg` for `/speckit` and `.specify`.
