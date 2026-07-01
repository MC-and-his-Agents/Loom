# Current Status

## Derived Fact Chain View

- Item ID: WI-1844
- Goal: 产品化 release readback 后的通用 release closeout-sync 入口。
- Scope: 实现 loom release closeout-sync dry-run/apply、CLI contract、README/README.zh-CN 和 CLI matrix；不发布、不 republish、不自动 merge、不新增 carrier/DSL。
- Execution Path: issue #1844 -> branch work/1844-release-closeout-sync -> PR -> v0.24.1 release
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1844.md
- Review Entry: .loom/reviews/WI-1844.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface release-readback; python3 tools/check_cli_contract.py --surface aggregate; loom release closeout-sync dogfood dry-run
- Closing Condition: PR merges, #1842/#1843/#1846 close, v0.24.1 publishes and release closeout-sync carrier is terminalized.
- Current Checkpoint: merge
- Current Stop: hosted `loom-check`/`node-installer-pr` 二次失败已分类为 `github-api-budget`：测试文件自身包含 forbidden `gh pr view` 字面量。已改为拼接 forbidden token，保留 contract 断言且不让高频路径出现该字面量；本地 py_compile、forbidden-token rg 和 release-readback contract 已通过。
- Next Step: 重新生成当前 head review/shadow，提交并推送修复，更新 PR #1847 metadata 到新 head，运行 PR gate，等待 hosted checks 后执行 merge check/run；v0.24.1 release 在实现 PR 合并后执行。
- Blockers: None recorded.
- Latest Validation Summary: py_compile_clean passed for tools/check_cli_contract.py; `rg -n "gh pr view" tools/loom.py tools/check_cli_contract.py` returned no matches; check_cli_contract --surface release-readback passed in 1.65s with host-binding PR readback coverage, published/idempotent, non-carrier-gap, PR-readback fail-closed, dry-run, apply, and drift coverage; earlier py_compile_clean passed for tools/loom.py and tools/check_cli_contract.py; earlier check_cli_contract --surface aggregate passed locally in 404.53s; suite validate, suite carrier validate, and suite evidence validate passed; dogfood release closeout-sync dry-run for v0.24.0/WI-1834/PR #1840 passed against main without carrier mutation.
- Recovery Boundary: WI-1844 owns release closeout-sync wrapper, docs, tests, and v0.24.1 convergence only; no publishing, republishing, GitHub Release/npm mutation, auto merge, multi-repo batch, new DSL, or new carrier in implementation PR.
- Current Lane: merge-ready

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1844 release closeout-sync work is active in `/Users/mc/dev/Loom.worktrees/1844-release-closeout-sync` on branch `work/1844-release-closeout-sync`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1844.md`.
- Diagnostics Entry: Release closeout-sync dogfood dry-run passes against the WI-1834 main worktree; the same command correctly fail-closes when run from the WI-1844 worktree against WI-1834 because the fact-chain item does not match.
- Verification Entry: `python3 tools/py_compile_clean.py tools/check_cli_contract.py`, `rg -n "gh pr view" tools/loom.py tools/check_cli_contract.py`, `python3 tools/check_cli_contract.py --surface release-readback`, suite validate, suite carrier validate, and release closeout-sync dogfood dry-run passed.
- Lane Entry: merge-ready

## Sources

- Static Truth: .loom/work-items/WI-1844.md
- Dynamic Truth: .loom/progress/WI-1844.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
