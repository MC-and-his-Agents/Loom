# Current Status

## Derived Fact Chain View

- Item ID: WI-1834
- Goal: 实现单仓 Loom 运行时升级维护流程，并为 v0.24.0 发布准备标准、低摩擦、可验证的 repo runtime pin 升级路径。
- Scope: 覆盖 issue #1834-#1838 的 runtime-upgrade status/prepare/check/closeout、loom -v/--version、CLI help/matrix、英文/中文 README、Codex plugin/cache advisory guidance、runtime copy/plugin metadata/hash 与示例 fixture 同步；不包含多仓批量升级或跳过治理。
- Execution Path: issue tree #1834 -> branch work/1834-runtime-upgrade -> PR #1839 -> merge -> v0.24.0 release #1838 -> closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1834.md
- Review Entry: .loom/reviews/WI-1834.json
- Validation Entry: make py-compile; make loom-demo-new-project-check; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/check_npm_package.py; python3 tools/check_npm_package.py --surface runtime-copy-parity; python3 tools/loom.py skills release-check --json; PR metadata preflight/readback for PR #1839
- Closing Condition: PR #1839 merges to main, #1835-#1837 implementation scope is closed, v0.24.0 release issue #1838 publishes and reads back GitHub/npm/package/plugin metadata, #1834-#1838 and milestone #20 close, and repo carrier closeout consumes the final facts.
- Current Checkpoint: merge
- Current Stop: Implementation PR #1839 has a current reviewed implementation head 6bebb4e6fa21ee6e82f2234a8792f825b1f9e5f3; runtime-upgrade implementation plus review checkpoint normalization, README/README.zh-CN sync, plugin metadata/hash refresh, and demo bootstrap fixture sync are committed locally. PR body/head readback must be refreshed after this carrier commit is pushed.
- Next Step: Commit and push the carrier refresh, update PR #1839 body to the final head, rerun PR metadata readback and hosted PR gate, merge PR #1839 when gates pass, then run #1838 v0.24.0 release/readback/closeout from main.
- Blockers: PR #1839 body and hosted PR gate must be refreshed after the carrier commit. v0.24.0 release remains blocked until PR #1839 merges.
- Latest Validation Summary: make py-compile; python3 tools/check_cli_contract.py --surface governance-closeout; python3 tools/check_npm_package.py; python3 tools/check_npm_package.py --surface runtime-copy-parity; python3 tools/loom.py resume --target . --item WI-1834 --json; git diff --check passed after normalizing review checkpoint to merge. Earlier runtime-upgrade, pr-metadata, aggregate, skills release-check, README/README.zh-CN, hosted loom-check, node-installer, and release-judgment evidence remain valid for the implementation surface.
- Recovery Boundary: WI-1834 owns single-repo runtime-upgrade maintenance flow implementation and v0.24.0 release convergence only. Do not add multi-repo batch mode, do not mutate user-level Codex plugin/cache from repo PR commands, do not lower review/PR gate/head binding/CI/release/closeout requirements, and do not represent plugin/cache advisory state as a repo merge fact.
- Current Lane: implementation-pr

## Runtime Evidence

- Run Entry: 2026-07-01 WI-1834 runtime-upgrade work resumed in `/Users/mc/dev/Loom.worktrees/1834-runtime-upgrade` on branch `work/1834-runtime-upgrade`.
- Logs Entry: Validation output and hosted check classification are retained in this Codex thread and summarized in `.loom/progress/WI-1834.md`.
- Diagnostics Entry: Hosted `loom-pr-merge-gate` first failed because it read stale PR body/head metadata before update propagation and because repo fact-chain/review still pointed at WI-1805. WI-1834 fact-chain and review carriers are now refreshed and must be consumed by a new gate run.
- Verification Entry: `make py-compile`, `make loom-demo-new-project-check`, `python3 tools/check_cli_contract.py --surface aggregate`, package checks, release-check, diff whitespace, PR metadata preflight/readback, and hosted `loom-check` component jobs passed for current or immediately preceding stable inputs.
- Lane Entry: implementation-pr

## Sources

- Static Truth: .loom/work-items/WI-1834.md
- Dynamic Truth: .loom/progress/WI-1834.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
