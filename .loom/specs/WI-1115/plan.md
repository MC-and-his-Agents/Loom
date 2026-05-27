# WI-1115 Plan

- Suite path: minimal
- Work Item: WI-1115

## Implementation

1. Replace the dry-run-only scaffold payload path with a shared minimal scaffold payload that can plan or apply.
2. Keep default scaffold invocation read-only and preserve the #1114 dry-run JSON contract.
3. For `--apply`, create only missing `.loom/specs/<item>/spec.md` and `.loom/specs/<item>/plan.md` files from `docs/methodology/templates/scaffold/`.
4. Report actual created locators, per-artifact `wrote` and `status` fields, and preserve-existing overwrite policy.
5. Fail closed before writes for traversal or absolute item locators, symlink scaffold paths, and non-file artifact placeholders.
6. Keep `--suite full` fail-closed until the full-artifact Work Item owns that surface.
7. Extend CLI contract checks for create, existing-file preservation, repeat apply, invalid item, symlink, non-file artifact, dry-run, and full-suite reserved behavior.
8. Record #1115 fact-chain carriers, spec review, implementation review, and status surface.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Apply Creates Missing Minimal Artifacts | `python3 tools/loom.py suite scaffold --target <tmp> --item WI-1115 --json --apply`; `python3 tools/check_cli_contract.py` |
| S2 Apply Preserves Existing Artifacts | `python3 tools/check_cli_contract.py` |
| S3 Repeat Apply Is A No-Op | `python3 tools/check_cli_contract.py` |
| S4 Full Suite Remains Reserved | `python3 tools/check_cli_contract.py` |
| S5 Unsafe Artifact Paths Fail Closed | `python3 tools/check_cli_contract.py`; targeted invalid item and symlink scaffold commands |

## Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py suite scaffold --target <tmp> --item WI-1115 --json --apply`
- targeted `suite scaffold --apply` checks for traversal item, absolute item, symlink artifact, and directory artifact fail-closed behavior
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` checks for suite scaffold apply anchors
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Boundaries

- No full suite artifact generation.
- No suite validate/analyze, evidence, consistency, or carrier subcommands.
- No GitHub issue, PR, Project, review, merge-ready, or closeout writes from the suite CLI.
- No generated skills mutation.
- No spec-kit command names or `.specify/` layout.
- No replacement of Work Item, review, merge-ready, closeout, Project, or docs/source truth.
