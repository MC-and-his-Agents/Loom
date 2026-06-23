# WI-1775 Plan

## Phases

- P1: Add first-class `closeout status` / `closeout sync` command routing and help matrix entries.
- P2: Compose PR metadata readback/update with existing closeout check/run helpers.
- P3: Add read-only terminal cleanup readback for issue worktree, local branch, remote branch, and main worktree dirty state.
- P4: Emit blocked/fixed/next_action diagnostics through agent-safe output and full output.
- P5: Add focused `closeout-wrapper` contract coverage and live closeout status smoke evidence.
- P6: Open PR, stabilize metadata/review, merge, and close out #1775 before #1776 consumes it.

## Scenario Mapping

- S1 -> P1, P2, P4, P5
- S2 -> P2, P4, P5
- S3 -> P2, P4, P5
- S4 -> P3, P4, P5
- S5 -> P3, P4

## Acceptance Mapping

- A1 -> structural check: `python3 tools/loom.py help --json` includes `closeout status` and `closeout sync`
- A2 -> test evidence: `python3 tools/check_cli_contract.py --surface closeout-wrapper`
- A3 -> test evidence: `assert_closeout_sync_status_contract`
- A4 -> test evidence: `assert_closeout_sync_status_contract`
- A5 -> test evidence: `assert_closeout_sync_status_contract`
- A6 -> test evidence: `assert_closeout_sync_status_contract`
- A7 -> test evidence: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface closeout-wrapper`; `git diff --check`

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1775 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1775 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1775 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1775 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout status --target . --item WI-1777 --issue 1777 --pr 1779 --branch work/1777-ship-preflight-status --head-sha c16c3e93c915574bff17629df8bc90a3e7c903d4 --json --full-output`
- `git diff --check`

## Deferred

- #1776 owns release readback verdict taxonomy and release closeout diagnostics.
- #1778 owns v0.21.0 release execution and terminal release closeout.
- #1774 parent backlog owns automatic host-safe worktree locator generation and destructive cleanup automation.
