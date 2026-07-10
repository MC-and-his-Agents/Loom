# WI-1777 Plan

## Phases

- P1: Add first-class `ship status` / `ship preflight` command routing and help matrix entries.
- P2: Add read-only status helpers for host issue/milestone, target release presence, checkout freshness, and `.loom/status/current.md`.
- P3: Emit blocked/fixed/next_action diagnostics through full output and agent-safe short output.
- P4: Add focused `ship-wrapper` contract coverage and live read-only smoke evidence.
- P5: Open PR, refresh metadata/review, merge, and close out #1777 before #1775 begins.

## Scenario Mapping

- S1 -> P2, P3, P4
- S2 -> P2, P3, P4
- S3 -> P2, P3, P4
- S4 -> P2, P3, P4
- S5 -> P1, P4

## Acceptance Mapping

- A1 -> structural check: `python3 tools/loom.py help --json` includes `ship status` and `ship preflight`
- A2 -> test evidence: `python3 tools/check_cli_contract.py --surface ship-wrapper`
- A3 -> test evidence: `assert_ship_status_preflight_contract`
- A4 -> test evidence: `assert_ship_status_preflight_contract`
- A5 -> test evidence: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface ship-wrapper`; `git diff --check`

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1777 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1777 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1777 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1777 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py ship preflight --target . --item WI-1777 --issue 1777 --milestone 18 --version v0.21.0 --package @mc-and-his-agents/loom --json --full-output`
- `git diff --check`

## Deferred

- #1775 owns mutating closeout sync, PR metadata race handling, and terminal cleanup check.
- #1776 owns release verdict taxonomy and multi-worktree merge fallback.
