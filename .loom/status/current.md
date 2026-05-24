# Current Status

## Derived Fact Chain View

- Item ID: WI-915
- Goal: 实现 #890/#891 的 CLI-first adoption/profile、fact-chain/status/checkpoint/gate 命令合同。
- Scope: 覆盖 #915-#923：init/adopt/route、profile status/upgrade-plan/upgrade、status/fact-chain、checkpoint admission/build/merge、gate pre-review/spec-review/review/pr/merge/closeout，以及 missing carrier / missing host input 的 fail-closed 合同。
- Execution Path: cli-first/adoption-profile-gates
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-915.md
- Review Entry: .loom/reviews/WI-915.json
- Validation Entry: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py profile status --target . --json; python3 tools/loom.py checkpoint admission --target . --item WI-915 --json; python3 tools/loom.py gate pr --target . --item WI-915 --json
- Closing Condition: PR 合并后关闭 #915-#923，并让 #890/#891 消费命令语义、JSON 输出、fail-closed、fallback、验证证据和 head_sha。
- Current Checkpoint: build checkpoint
- Current Stop: #890/#891 command wrappers, contract checks, docs, and WI carriers are ready for review.
- Next Step: Record review carriers, open PR, run PR gate/CI, then merge after required checks pass.
- Blockers: None recorded.
- Latest Validation Summary: Passed on branch work/890-891-adoption-gates: python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_flow.py shadow-parity --target .
- Recovery Boundary: WI-915 owns the #890/#891 batch for #915-#923 only. It does not implement unrelated profile finalization, bottom-layer GitHub/CI/review/worktree rewrites, repo-specific guardian replacement, or mutating closeout/merge execution.
- Current Lane: cli-first/adoption-profile-gates

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: make loom-check-runtime-regression; make py-compile; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main; make loom-check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-915.md
- Dynamic Truth: .loom/progress/WI-915.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
