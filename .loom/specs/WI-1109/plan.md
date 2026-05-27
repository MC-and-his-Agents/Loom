# WI-1109 Plan

## Implementation Target

Add the first `suite inspect` read-only command path to `tools/loom.py` and cover its unknown-state behavior in `tools/check_cli_contract.py`.

## Phases

1. Add root `suite` command dispatch.
2. Implement `suite inspect` argument parsing and JSON envelope.
3. Add a CLI contract fixture for unknown state and no mutation.
4. Run focused and source-surface validation.

## Constraints

- Ownership is limited to `tools/loom.py`, `tools/check_cli_contract.py`, and WI-1109 local Loom carriers.
- The command must not write files or mutate host state.
- The command must not implement later FR behavior.

## Validation Strategy

| Scenario | Validation |
| --- | --- |
| S-1109-1 | `python3 tools/loom.py suite inspect --target . --item WI-1109 --json` and `python3 tools/check_cli_contract.py` |
| S-1109-2 | CLI contract fixture compares target directory contents before and after inspect |

## Test Strategy

| Acceptance | Evidence |
| --- | --- |
| AC-1109-1 | `python3 tools/check_cli_contract.py` |
| AC-1109-2 | direct `suite inspect` smoke and CLI contract fixture |
| AC-1109-3 | CLI contract no-mutation assertion |

## Verification Evidence

- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1109 --json`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
