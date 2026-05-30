# Implementation Contract

## Ownership

- Owns #1153 integration fixture behavior and WI-1153 carriers.
- Does not own #1152 worktree, branch, generated skills parity fixture scope, parent #1145 closeout, #1107 closeout, Project mutation, or merge.

## Guardrails

- No spec-kit `/speckit.*` command names.
- No `.specify/` layout.
- CLI output remains evidence only and does not replace Work Item, review, merge-ready, closeout, issue, Project, docs, or source truth.
- Fixtures must be non-mutating unless an existing harness path explicitly supports mutation.
- #1014-#1020 frozen core contracts must not be rewritten.

## Required Local Validation

- `git diff --check`
- focused `rg` for WI-1153, PR gate, merge-ready, closeout, Project, merge commit, target branch, PR merged alone, `/speckit`, and `.specify`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- focused closeout/reconciliation/gate fixture commands
