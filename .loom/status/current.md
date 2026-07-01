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
- Current Stop: 实现、spec review、implementation review、PR metadata readback、本地 review flow、targeted/aggregate/suite/evidence 验证均已通过；hosted gate 的本机绝对 workspace locator 已修正为 repo-relative `.`，等待最新 carrier head 重新通过 hosted checks 和 merge check。
- Next Step: 提交 portable workspace carrier 修正，更新 PR metadata 到新 head，运行 PR gate、等待 hosted checks、执行 merge check/run；v0.24.1 release 在实现 PR 合并后执行。
- Blockers: None recorded.
- Latest Validation Summary: py_compile_clean passed; check_cli_contract --surface release-readback passed in 1.61s with published/idempotent, non-carrier-gap, PR-readback fail-closed, dry-run, apply, and drift coverage; check_cli_contract --surface aggregate passed locally at current head in 404.53s; suite validate, suite carrier validate, and suite evidence validate passed; dogfood release closeout-sync dry-run for v0.24.0/WI-1834/PR #1840 passed against main without carrier mutation; cross-item WI-1844 target correctly failed closed.
- Recovery Boundary: WI-1844 owns release closeout-sync wrapper, docs, tests, and v0.24.1 convergence only; no publishing, republishing, GitHub Release/npm mutation, auto merge, multi-repo batch, new DSL, or new carrier in implementation PR.
- Current Lane: merge-ready

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1844 release closeout-sync work is active in `/Users/mc/dev/Loom.worktrees/1844-release-closeout-sync` on branch `work/1844-release-closeout-sync`.
- Logs Entry: Validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1844.md`.
- Diagnostics Entry: Release closeout-sync dogfood dry-run passes against the WI-1834 main worktree; the same command correctly fail-closes when run from the WI-1844 worktree against WI-1834 because the fact-chain item does not match.
- Verification Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`, `python3 tools/check_cli_contract.py --surface release-readback`, suite validate, suite carrier validate, and release closeout-sync dogfood dry-run passed.
- Lane Entry: implementation-ready

## Sources

- Static Truth: .loom/work-items/WI-1844.md
- Dynamic Truth: .loom/progress/WI-1844.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
