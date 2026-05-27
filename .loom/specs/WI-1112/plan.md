# WI-1112 Plan

- Suite path: minimal
- Work Item: WI-1112

## Implementation

1. Add a shared target snapshot helper in `tools/check_cli_contract.py`.
2. Route every suite inspect fixture through a shared helper that verifies the command envelope, item binding, `mutates: false`, and no target mutation.
3. Keep existing unknown, minimal, full, and missing required artifact payload assertions.
4. Add not_applicable fixture coverage for the implemented suite path marker branch.
5. Record #1112 fact-chain carriers, spec review, implementation review, and status surface.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Unknown State Is Read-Only | `python3 tools/check_cli_contract.py` |
| S2 Minimal State Is Read-Only | `python3 tools/check_cli_contract.py` |
| S3 Full State Is Read-Only | `python3 tools/check_cli_contract.py` |
| S4 Missing Required Artifact Is Read-Only | `python3 tools/check_cli_contract.py` |
| S5 Not Applicable Branch Is Guarded | `python3 tools/check_cli_contract.py` |

## Commands

- `python3 tools/py_compile_clean.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1112 --json`
- `git diff --check`
- focused `rg` checks for suite inspect fixture anchors
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
- No replacement of Work Item, review, merge-ready, closeout, Project, or docs/source truth.
