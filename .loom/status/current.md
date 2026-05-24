# Current Status

## Derived Fact Chain View

- Item ID: WI-906
- Goal: 实现 `loom detect --target`，并推进 #888 detect/doctor/repair 批次到可验证状态
- Scope: 覆盖 #888 的 #906-#909：installed surface detection、doctor JSON、non-mutating repair plan、repair apply fail-closed、WebEnvoy/Syvert/HotCP legacy detect synthetic fixtures；不实现 installer shim、host/skills 编排或 mutating repair apply。
- Execution Path: cli-first/detect-doctor-repair
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-906.md
- Review Entry: .loom/reviews/WI-906.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; make check
- Closing Condition: PR 合并后关闭 #906-#909，并让 #888 能消费命令语义、JSON 输出、fail-closed、fallback、验证证据和 head_sha。
- Current Checkpoint: merge-ready checkpoint
- Current Stop: #888 detect/doctor/repair implementation, docs, fixtures, and WI carriers are ready for PR creation.
- Next Step: Create PR, run PR gate/CI, then merge after required checks pass.
- Blockers: None recorded.
- Latest Validation Summary: Passed on branch work/888-detect-doctor-repair: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py detect --target . --json; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-906; python3 .loom/bin/loom_flow.py shadow-parity --target .; make check with loom_check OK over 40 source/distribution surfaces.
- Recovery Boundary: WI-906 owns the #888 batch for #906-#909 only: detect, doctor, repair plan, repair apply fail-closed, and legacy detect fixtures. Later #893/#894/#895 installer shim, host, and skills orchestration remain reserved.
- Current Lane: cli-first/detect-doctor-repair

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check-runtime-regression; make py-compile; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main; make loom-check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-906.md
- Dynamic Truth: .loom/progress/WI-906.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
