# Current Status

## Derived Fact Chain View

- Item ID: WI-1777
- Goal: 实现 `loom ship status` / `loom ship preflight` 一次性现场读回。
- Scope: Issue #1777: add a read-only ship preflight/status surface that reports blocking issue/milestone, target release presence, checkout freshness, and carrier active/terminal state with short blocked/fixed/next_action diagnostics. Ownership is limited to `tools/loom.py`, `tools/check_cli_contract.py`, WI-1777 carriers, `.loom/specs/WI-1777`, and the `.loom/progress/WI-1714.md` terminal carrier repair required to keep hosted workspace purity after issue #1714 closed and PR #1724 merged.
- Execution Path: issue #1777 -> branch work/1777-ship-preflight-status -> PR pending -> controlled merge -> closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1777.md
- Review Entry: .loom/reviews/WI-1777.json
- Validation Entry: `git diff --check`; `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface ship-wrapper`; live `loom.py ship preflight` read-only smoke.
- Closing Condition: PR merged and issue #1777 closed with ship preflight/status evidence consumed by #1775.
- Current Checkpoint: merge
- Current Stop: PR #1779 is open for #1777, metadata is bound to head 271ada5bf92c2ac6f95170676c964389b2945a3a, local validation is passing, and merge-ready readback is consuming hosted gate results.
- Next Step: Push the WI-1714 terminal checkpoint repair, refresh PR metadata/readback to the new head, wait for hosted checks, merge PR #1779, then close out #1777 before #1775 begins.
- Blockers: none
- Latest Validation Summary: 2026-06-23 local validation passed on branch `work/1777-ship-preflight-status`: git diff --check; python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface ship-wrapper; python3 tools/loom.py suite validate --target . --item WI-1777 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1777 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1777 --json; python3 tools/loom.py fact-chain --target . --item WI-1777 --json; python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking; python3 tools/loom.py help --json | rg -n 'ship status|ship preflight|ship"'; python3 tools/loom.py ship preflight --target . --item WI-1777 --issue 1777 --milestone 18 --version v0.21.0 --package @mc-and-his-agents/loom --json --full-output. 2026-06-23 readback confirmed WI-1714 is terminal after changing `.loom/progress/WI-1714.md` checkpoint from non-terminal `closeout` to canonical terminal `merged`.
- Recovery Boundary: WI-1777 owns ship status/preflight readback and diagnostics plus the WI-1714 terminal carrier repair required to unblock hosted purity only; it does not implement closeout sync, release verdict, merge fallback, publishing, or any new #1714 behavior.
- Current Lane: ship-preflight-status

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1777 implementation started in `/Users/mc/dev/Loom-WI-1777-ship-preflight-status` on branch `work/1777-ship-preflight-status`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1777.md`.
- Diagnostics Entry: `loom ship status` / `loom ship preflight` emit read-only blocked/fixed/next_action diagnostics for checkout, release, host, and carrier drift.
- Verification Entry: py compile, ship-wrapper contract, diff check, and live preflight smoke passed.
- Lane Entry: ship-preflight-status

## Sources

- Static Truth: .loom/work-items/WI-1777.md
- Dynamic Truth: .loom/progress/WI-1777.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
