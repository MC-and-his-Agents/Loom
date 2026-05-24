# Current Status

## Derived Fact Chain View

- Item ID: WI-929
- Goal: 实现 #893/#894/#895 的 CLI-first 控制面、host adapter 编排和 SKILLS surface 命令合同。
- Scope: 覆盖 #929-#943：workspace、issue、project、PR、merge、reconcile、host list/doctor/install/verify/upgrade/remove、skills list/generate/sync/check/doctor/package/release-check；冻结 JSON 输出、fail-closed、fallback 与验证证据。
- Execution Path: cli-first/control-host-skills
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-929.md
- Review Entry: .loom/reviews/WI-929.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py host doctor --host codex --target . --json; python3 tools/loom.py skills release-check --json; make check
- Closing Condition: PR 合并后关闭 #929-#943，并让 #893/#894/#895 消费命令语义、JSON 输出、fail-closed、fallback、验证证据和 head_sha。
- Current Checkpoint: merge-ready checkpoint
- Current Stop: #893/#894/#895 command implementation, docs, fixtures, and WI carriers are ready for PR creation.
- Next Step: Create PR, run PR gate/CI, then merge after required checks pass.
- Blockers: None recorded.
- Latest Validation Summary: Passed on branch work/893-895-cli-orchestration: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py host doctor --host codex --target . --json; python3 tools/loom.py skills release-check --json; python3 tools/loom.py workspace check --target . --item WI-929 --json; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-929; python3 .loom/bin/loom_flow.py shadow-parity --target .; npm test --prefix packages/loom-installer; make check with loom_check OK over 40 source/distribution surfaces.
- Recovery Boundary: WI-929 owns the #893/#894/#895 batch for #929-#943 only. It does not implement unrelated profile finalization, bottom-layer GitHub/CI/review/worktree rewrites, repo-specific guardian replacement, or mutating host remove semantics.
- Current Lane: cli-first/control-host-skills

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check-runtime-regression; make py-compile; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main; make loom-check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-929.md
- Dynamic Truth: .loom/progress/WI-929.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
