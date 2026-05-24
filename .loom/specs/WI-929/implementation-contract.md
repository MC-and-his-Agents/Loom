# WI-929 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `docs/methodology/harness/cli-first-control-plane.md`
- `.loom/work-items/WI-929.md`
- `.loom/progress/WI-929.md`
- `.loom/progress/WI-906.md`
- `.loom/reviews/WI-929.json`
- `.loom/reviews/WI-929.spec.json`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Required Evidence

- `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom.py host doctor --host codex --target . --json`
- `python3 tools/loom.py skills release-check --json`
- `make check`

## Non-Goals

- No bottom-layer GitHub, CI, code review, or worktree reimplementation.
- No profile finalization.
- No repo-specific guardian replacement.
- No host remove mutation without a later rollback/delete ownership contract.
