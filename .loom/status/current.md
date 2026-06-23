# Current Status

## Derived Fact Chain View

- Item ID: WI-1775
- Goal: 实现 `loom closeout status` / `loom closeout sync` 消费 merged PR 与 terminal carrier。
- Scope: Issue #1775: add a closeout readback and sync surface that reads PR metadata, host closeout state, terminal carrier status, and cleanup state; it may apply PR metadata stabilization and existing closeout reconciliation when explicitly invoked with `--apply`. Ownership is limited to `tools/loom.py`, `tools/check_cli_contract.py`, WI-1775 carriers, `.loom/specs/WI-1775`, and `.loom/reviews/WI-1775.json`.
- Execution Path: issue #1775 -> branch work/1775-closeout-sync -> PR pending -> controlled merge -> closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1775.md
- Review Entry: .loom/reviews/WI-1775.json
- Validation Entry: `git diff --check`; `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface closeout-wrapper`; closeout sync/status smoke.
- Closing Condition: PR merged and issue #1775 closed with closeout sync evidence consumed by #1776.
- Current Checkpoint: merge
- Current Stop: PR #1781 metadata, review evidence, and hosted merge gate are being stabilized for branch `work/1775-closeout-sync`.
- Next Step: Wait for hosted checks to consume PR head 859c5ef6daeb8c0cf1454b851cf7b0a8f6689c47, then merge PR #1781 and run closeout sync.
- Blockers: none
- Latest Validation Summary: 2026-06-23 local validation passed on branch `work/1775-closeout-sync`: git diff --check; python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface closeout-wrapper; python3 tools/loom.py suite validate --target . --item WI-1775 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1775 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1775 --json; python3 tools/loom.py fact-chain --target . --item WI-1775 --json; python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking; python3 tools/loom.py help --json | rg -n 'closeout status|closeout sync|closeout run|closeout"'; python3 tools/loom.py closeout status --target . --item WI-1777 --issue 1777 --pr 1779 --branch work/1777-ship-preflight-status --head-sha c16c3e93c915574bff17629df8bc90a3e7c903d4 --skip-metadata --json --full-output. 2026-06-23 readback without --skip-metadata on historical PR #1779 produced the expected metadata-readback blocker because #1779 predates closeout-surface machine metadata.
- Recovery Boundary: WI-1775 owns closeout status/sync readback, PR metadata race stabilization before closeout consumption, terminal cleanup readback, its spec/review/status carriers, and targeted closeout-wrapper regression coverage only. It does not implement release readback verdicts, publishing, automatic branch deletion, worktree deletion, or new release closeout behavior.
- Current Lane: closeout-sync

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1775 implementation started in `/Users/mc/dev/Loom-WI-1775-closeout-sync` on branch `work/1775-closeout-sync`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1775.md`.
- Diagnostics Entry: `loom closeout status` / `loom closeout sync` emit blocked/fixed/next_action diagnostics for closeout metadata, host closeout reconciliation, carrier sync, and terminal cleanup readback.
- Verification Entry: py compile, closeout-wrapper contract, suite/fact-chain/shadow checks, diff check, and closeout status smoke passed.
- Lane Entry: closeout-sync

## Sources

- Static Truth: .loom/work-items/WI-1775.md
- Dynamic Truth: .loom/progress/WI-1775.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
