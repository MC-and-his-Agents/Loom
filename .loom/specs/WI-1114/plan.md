# WI-1114 Plan

- Suite path: minimal
- Work Item: WI-1114

## Implementation

1. Add `suite scaffold` to the mechanical CLI command matrix and human command matrix.
2. Add a dry-run scaffold payload helper that plans `.loom/specs/<item>/spec.md` and `.loom/specs/<item>/plan.md`.
3. Include source template locators from `docs/methodology/templates/scaffold/`, consumed contract locators, overwrite policy, rollback note, and empty `created_locators`.
4. Route `loom suite scaffold` through `handle_suite` with `--apply` and `--suite full` fail-closed.
5. Add CLI contract fixtures that assert no target mutation, stable JSON output, existing-file preservation, and reserved fail-closed behavior.
6. Record #1114 fact-chain carriers, spec review, implementation review, and status surface.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Minimal Dry-Run Plans Writes | `python3 tools/loom.py suite scaffold --target . --item WI-1114 --json`; `python3 tools/check_cli_contract.py` |
| S2 Existing Files Are Preserved | `python3 tools/check_cli_contract.py` |
| S3 Apply Is Reserved | `python3 tools/check_cli_contract.py` |
| S4 Full Suite Is Reserved | `python3 tools/check_cli_contract.py` |

## Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py suite scaffold --target . --item WI-1114 --json`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` checks for suite scaffold anchors
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Boundaries

- No `--apply` writes.
- No full suite artifact generation.
- No suite validate/analyze, evidence, consistency, or carrier subcommands.
- No GitHub issue, PR, Project, review, merge-ready, or closeout writes from the suite CLI.
- No generated skills mutation.
- No spec-kit command names or `.specify/` layout.
- No replacement of Work Item, review, merge-ready, closeout, Project, or docs/source truth.
