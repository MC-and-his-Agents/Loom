# WI-1844 Implementation Contract

## Scope

- Runtime owner: `tools/loom.py`.
- Contract regression owner: `tools/check_cli_contract.py`.
- Documentation owner: `README.md`, `README.zh-CN.md`, and `docs/methodology/harness/cli-command-matrix.md`.
- Loom carrier owner: `.loom/work-items/WI-1844.md`, `.loom/progress/WI-1844.md`, `.loom/status/current.md`, `.loom/reviews/WI-1844.json`, and `.loom/specs/WI-1844/*`.

## Required Behavior

- `loom release closeout-sync` defaults to dry-run.
- The command may proceed only when release readback is `published` or blocked solely by `carrier_not_terminal`.
- `--apply` may write only repo carrier surfaces: closeout progress metadata, status sync, and closeout/merge-ready shadow refresh.
- Release drift, missing release artifacts, workflow failure, unreadable PR, unmerged PR, or release PR merge commit mismatch must fail closed before carrier writes.
- The command must output post-commit PR metadata, PR gate, merge check, and post-merge release readback next commands.

## Non-Goals

- No publishing or republishing.
- No tag, GitHub Release, npm, workflow, or package registry mutation.
- No automatic PR merge.
- No multi-repo batch mode.
- No new carrier or policy DSL.
- No Loom-repository-specific release knowledge.

## Validation Contract

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1844 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1844 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1844 --json`
- Dogfood dry-run against the WI-1834 main worktree for v0.24.0 / PR #1840.

## Review Boundary

Review consumes the focused release closeout-sync wrapper, CLI contract assertions, dogfood dry-run, and documentation boundary updates. Any expansion into publishing, republishing, GitHub Release/npm mutation, automatic merge, multi-repo orchestration, new carrier/DSL, or release policy semantics requires a separate Work Item.
