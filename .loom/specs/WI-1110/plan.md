# WI-1110 Plan

- Suite path: minimal
- Work Item: WI-1110

## Implementation

1. Add conservative suite discovery helpers near `handle_suite`.
2. Prefer explicit `suite-index.md` path decisions, then explicit `spec.md` / `plan.md` markers.
3. Build artifact inventory from the current Work Item suite root.
4. Keep required artifact gaps inspect-only by reporting them in payload `missing_inputs` and `advisory_gaps`.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Unknown Suite | Existing empty target fixture in `tools/check_cli_contract.py` |
| S2 Minimal Suite Locators | Temp minimal fixture with `spec.md` and `plan.md` |
| S3 Full Suite Locators | Temp full fixture with suite index and optional artifacts |
| S4 Missing Expected Artifact | Temp full fixture missing `plan.md` |

## Commands

- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1110 --json`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` checks for suite locator anchors
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`

## Boundaries

- No readiness validation.
- No scaffold writes.
- No host mutation.
- No spec-kit command names or `.specify/` layout.
