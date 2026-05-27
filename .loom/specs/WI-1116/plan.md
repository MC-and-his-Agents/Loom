# WI-1116 Plan

- Suite path: minimal
- Work Item: WI-1116

## Implementation

1. Generalize the scaffold artifact catalog so minimal and full suite paths share the same planning and apply pipeline.
2. Map full suite destination artifact `suite-index.md` to template `docs/methodology/templates/scaffold/full-suite-index.md`.
3. Add required and conditional artifact metadata to the scaffold payload.
4. Remove the `--suite full` reserved-surface branch and let full suite dry-run/apply use the shared fail-closed safety checks.
5. Preserve the existing item segment validation, symlink traversal checks, non-file artifact checks, preserve-existing overwrite policy, and actual `created_locators` semantics.
6. Extend CLI contract checks for full dry-run, full apply, full preserve-existing, full repeat no-op, and full fail-closed safety coverage.
7. Update the CLI command matrix and #1116 fact-chain carriers.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Full Dry-Run Plans Standard Artifacts | `python3 tools/check_cli_contract.py`; targeted `loom suite scaffold --suite full --json` |
| S2 Full Apply Creates Missing Artifacts | `python3 tools/check_cli_contract.py`; targeted `loom suite scaffold --suite full --json --apply` |
| S3 Full Apply Preserves Existing Artifacts | `python3 tools/check_cli_contract.py` |
| S4 Repeat Full Apply Is A No-Op | `python3 tools/check_cli_contract.py` |
| S5 Unsafe Full Scaffold Paths Fail Closed | `python3 tools/check_cli_contract.py`; targeted symlink and invalid item checks |

## Commands

- `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py suite scaffold --target <tmp> --item WI-1116 --suite full --json`
- `python3 tools/loom.py suite scaffold --target <tmp> --item WI-1116 --suite full --json --apply`
- `python3 tools/check_cli_contract.py`
- `git diff --check`
- focused `rg` checks for full suite scaffold anchors
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Boundaries

- No user-authored spec content is produced; scaffold files are templates only.
- No evidence-map, consistency-analysis, execution breakdown, or task-carrier generation.
- No suite validate/analyze or evidence subcommands.
- No GitHub issue, PR, Project, review, merge-ready, or closeout writes from the suite CLI.
- No generated skills mutation.
- No spec-kit command names or `.specify/` layout.
- No replacement of Work Item, review, merge-ready, closeout, Project, or docs/source truth.

## Subagent Output Integration

- Sagan performed read-only #1116 surface analysis.
- Consumed conclusion: #1116 full scaffold owns exactly six standard artifacts; evidence/consistency/task-carrier surfaces remain later extension work.
- Integration owner: main agent.
