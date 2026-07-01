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
- Current Stop: hosted `loom-pr-merge-gate` 在 head `eec35d1` 重复暴露 `head_sha_drift`：PR body metadata 未绑定当前 head。已在该 gate 失败路径加入最小提示，要求先执行 metadata-update/readback 绑定当前 head，再 rerun failed hosted gate；不新增调度系统或 DSL。
- Next Step: 提交并推送 hosted gate head-drift 提示修复，重新绑定 review/shadow 和 PR #1847 metadata 到新 head，运行本地 PR gate，rerun/等待 hosted checks 后执行 merge check/run；v0.24.1 release 在实现 PR 合并后执行。
- Blockers: None recorded.
- Latest Validation Summary: hosted run 28499745738/job 84474000577 classified repeated `head_sha_drift`; py_compile_clean passed for tools/loom.py and tools/check_cli_contract.py; check_release_surface passed; YAML parse passed for .github/workflows/pr-merge-gate.yml; `rg -n "gh pr view" tools/loom.py tools/check_cli_contract.py` returned no matches; earlier check_cli_contract --surface release-readback passed with host-binding PR readback coverage; earlier check_cli_contract --surface aggregate passed locally in 404.53s; suite validate, suite carrier validate, suite evidence validate, and dogfood release closeout-sync dry-run passed.
- Recovery Boundary: WI-1844 owns release closeout-sync wrapper, docs, tests, and v0.24.1 convergence only; no publishing, republishing, GitHub Release/npm mutation, auto merge, multi-repo batch, new DSL, or new carrier in implementation PR.
- Current Lane: merge-ready

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1844 release closeout-sync work is active in `/Users/mc/dev/Loom.worktrees/1844-release-closeout-sync` on branch `work/1844-release-closeout-sync`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1844.md`.
- Diagnostics Entry: Release closeout-sync dogfood dry-run passes against the WI-1834 main worktree; the same command correctly fail-closes when run from the WI-1844 worktree against WI-1834 because the fact-chain item does not match.
- Verification Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`, `python3 tools/check_release_surface.py`, YAML parse for `.github/workflows/pr-merge-gate.yml`, `rg -n "gh pr view" tools/loom.py tools/check_cli_contract.py`, `python3 tools/check_cli_contract.py --surface release-readback`, suite validate, suite carrier validate, and release closeout-sync dogfood dry-run passed.
- Lane Entry: merge-ready

## Sources

- Static Truth: .loom/work-items/WI-1844.md
- Dynamic Truth: .loom/progress/WI-1844.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
