# Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1149/spec.md
- Plan locator: .loom/specs/WI-1149/plan.md
- Story Readiness consumed state: #1149 issue body
- Story Business Confirmation consumed state: not required because this is governance regression behavior.
- Freshness rule: refresh .loom/progress/WI-1149.md after final validation and before PR handoff.

## Phases

### Phase 1

- Objective: Tighten suite validate missing-input output for invalid skip records.
- Deliverable: `tools/loom.py` records missing skip fields in `missing_inputs`.
- Exit condition: focused negative fixture commands expose the expected missing inputs.

### Phase 2

- Objective: Add CLI contract negative fixture assertions.
- Deliverable: `tools/check_cli_contract.py` asserts missing required artifact and invalid skip-rationale fail-closed payloads.
- Exit condition: `python3 tools/check_cli_contract.py` passes.

### Phase 3

- Objective: Add source/installed loom_check regression coverage and synchronize generated surfaces.
- Deliverable: shared runtime helper validates the negative fixtures in source and installed paths.
- Exit condition: `python3 tools/skills_surface.py check` and focused loom_check profiles pass.

## Validation

- Scenario mapping:
  - S1 -> automated validation evidence: CLI contract missing artifact fixture and loom_check negative fixture.
  - S2 -> automated validation evidence: CLI contract invalid skip-rationale fixture and loom_check negative fixture.
- Acceptance mapping:
  - A1 -> test evidence: `python3 tools/check_cli_contract.py`.
  - A2 -> test evidence: source-self fixture check.
  - A3 -> test evidence: `python3 tools/skills_surface.py check`, py_compile, and runtime hash verification.
  - A4 -> structural evidence: focused `rg` for `/speckit` and `.specify`.
