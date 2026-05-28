# WI-1123 Plan

## Implementation Goal

Extend `loom suite validate` so it can detect missing `spec.md` scenario / acceptance consumption in `plan.md` before formal review.

## Phases

- Phase 1: Add a read-only parser for scenario and acceptance ids in `spec.md`.
- Phase 2: Add `plan.md` mapping detection for validation and test strategy rows.
- Phase 3: Emit structured blocking gaps and contract fixture coverage.
- Phase 4: Refresh source docs and Loom carriers without touching generated skill/runtime surfaces.

## Constraints

- Keep the parser conservative and fixture-driven; do not invent missing scenario or acceptance criteria.
- Preserve existing `suite validate` result envelope and current #1120-#1122 behavior.
- Do not integrate with spec-review gates in this Work Item.

## Validation

- Scenario validation mapping:
  - AC-1123-1 -> automated: python3 tools/check_cli_contract.py full path pass fixture.
  - AC-1123-2 -> automated: python3 tools/check_cli_contract.py missing scenario mapping fixture.
  - AC-1123-3 -> automated: python3 tools/check_cli_contract.py missing acceptance mapping fixture.
  - AC-1123-4 -> structural: focused rg for `spec_plan_mapping` and `missing_spec_plan_mapping`.
  - AC-1123-5 -> automated: existing suite validate fixtures in python3 tools/check_cli_contract.py.
- Fresh verification evidence:
  - git diff --check
  - python3 tools/skills_surface.py check
  - python3 tools/loom_check.py --profile source --source-surface contract-only .

## Test Strategy

- Acceptance test mapping:
  - AC-1123-1 -> test evidence: `suite_full_validate` fixture remains pass.
  - AC-1123-2 -> test evidence: `suite_full_missing_scenario` fixture blocks.
  - AC-1123-3 -> test evidence: `suite_full_missing_acceptance` fixture blocks.
  - AC-1123-4 -> structural check: payload assertions inspect `spec_plan_mapping`.
  - AC-1123-5 -> regression evidence: existing unknown/conflict/minimal/not_applicable/deferred/full missing artifact fixtures still pass.

## Ready For Implementation

- [x] Scope and non-goals are clear.
- [x] Validation path is defined.
- [x] BDD outer-loop scenarios map to validation evidence.
- [x] TDD inner-loop expectations map to test evidence.
