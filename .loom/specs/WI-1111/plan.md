# WI-1111 Plan

- Suite path: minimal
- Work Item: WI-1111

## Implementation

1. Add `suite inspect` to the frozen `COMMANDS` matrix in `tools/loom.py`.
2. Route the two-word command form back through the existing `handle_suite(["inspect", ...])` implementation.
3. Require `suite inspect` in `tools/check_cli_contract.py` and assert the matrix declaration.
4. Update `docs/methodology/harness/cli-command-matrix.md` so `suite inspect` is no longer described as planning-only.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Help JSON Declares Command | `python3 tools/loom.py help --json` and focused `rg` |
| S2 CLI Contract Guards Declaration | `python3 tools/check_cli_contract.py` |
| S3 Existing Inspect Behavior Remains Stable | Existing unknown/minimal/full/missing fixtures in `tools/check_cli_contract.py` |

## Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py suite inspect --target . --item WI-1111 --json`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` checks for suite inspect declaration anchors
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`

## Boundaries

- No new suite subcommands.
- No readiness validation.
- No scaffold writes.
- No host mutation.
- No spec-kit command names or `.specify/` layout.
