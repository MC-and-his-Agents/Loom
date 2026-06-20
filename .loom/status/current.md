# Current Status

## Derived Fact Chain View

- Item ID: WI-1624-1625-1627-1640
- Goal: 完成 milestone #14 PR1：硬切 `loom install` 为 metadata-only adoption，改造 installed-state 生成/校验只接受全局 provider，并让 detect/doctor 对旧 repo-local runtime/plugin/skills 安装面 fail closed。
- Scope: issue #1624、#1625、#1627、#1640；允许修改 `tools/loom.py`、`tools/check_cli_contract.py`、本 Work Item carrier，以及 gate 消费所需的 `.loom/shadow/merge-ready-loom.json`、`.loom/shadow/closeout-loom.json` source hash refresh。
- Execution Path: issue #1624/#1625/#1627/#1640 -> branch `work/1624-global-install-cutover` -> PR1 -> targeted checks -> hosted gate -> merge -> issue closeout。
- Workspace Entry: .
- Recovery Entry: `.loom/progress/WI-1624-1625-1627-1640.md`
- Review Entry: `.loom/reviews/WI-1624-1625-1627-1640.json`
- Validation Entry: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate`; `make py-compile`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `git diff --check`
- Closing Condition: PR1 merges into `main`, issues #1624/#1625/#1627/#1640 are closed or linked to the merged PR, and repo carriers consume the merge/head/check evidence without starting PR2.
- Current Checkpoint: merge
- Current Stop: PR1 implementation and semantic review are ready for merge-ready / PR gate consumption on branch `work/1624-global-install-cutover`.
- Next Step: run merge-ready / PR gate for PR #1649, then merge and close issues #1624/#1625/#1627/#1640 without starting PR2.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20T03:12Z local validation passed: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate` passed in 341.37s; `make py-compile`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/loom.py suite carrier validate --target . --item WI-1624-1625-1627-1640 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1624-1625-1627-1640 --json`; `python3 tools/loom.py suite validate --target . --item WI-1624-1625-1627-1640 --json`; `git diff --check`. Smoke checks confirmed `loom install --help` no longer exposes `--mode`, dry-run planned writes are `.loom/installed-state.json` and `AGENTS.md`, `loom install --mode plugin` exits non-zero, and `.loom/bin` with current installed-state makes `doctor` block as legacy residue.
- Recovery Boundary: PR1 only. Do not implement Codex user-level plugin install/register, plugin payload generation, single-skill deletion, package surface cleanup, v0.17.0 release judgment, or release execution in this Work Item.
- Current Lane: milestone-14-pr1-global-install-cutover

## Runtime Evidence

- Run Entry: 2026-06-20 WI-1624-1625-1627-1640 PR1 local build
- Logs Entry: local command output retained in current Codex milestone/14 thread
- Diagnostics Entry: PR1 consumes completed contract lane #1621/#1622/#1623/#1628/#1638 and does not start PR2.
- Verification Entry: CLI contract, py_compile, host adapter check, release surface check, diff hygiene, and smoke commands passed locally on 2026-06-20.
- Lane Entry: milestone-14-pr1-global-install-cutover

## Sources

- Static Truth: .loom/work-items/WI-1624-1625-1627-1640.md
- Dynamic Truth: .loom/progress/WI-1624-1625-1627-1640.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
