# Current Status

## Derived Fact Chain View

- Item ID: WI-1629
- Goal: 完成 milestone #14 PR3：实现 Codex 用户级 plugin 纯全局安装与注册；loom host install/register --host codex --scope user 默认从全局 Loom 包读取 plugin payload，只写用户级 Codex 状态，不写目标仓库。
- Scope: issue #1629；允许修改 root CLI host install/register 实现、CLI contract 测试、本 Work Item carrier 和必要的最小 issue/PR metadata；不实现 repo adoption、CLI command matrix 删除、package surface 收敛、migration 文档或 v0.17.0 发布。
- Execution Path: issue #1629 -> branch work/1629-global-codex-plugin-install -> PR3 -> targeted CLI contract checks -> hosted gate -> merge -> issue closeout。
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1629.md
- Review Entry: .loom/reviews/WI-1629.json
- Validation Entry: python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py; python3 tools/host_adapter_check.py; python3 tools/check_npm_package.py; python3 tools/check_release_surface.py; node --test test/npm-package-smoke.test.mjs; python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; git diff --check
- Closing Condition: PR3 merges into main, issue #1629 closes against the merged PR, and closeout check consumes PR/head/check evidence without starting PR4.
- Current Checkpoint: build checkpoint
- Current Stop: PR3 implementation is complete locally: host install/register now defaults to the global Loom package Codex plugin payload and writes only user-level Codex state; contract tests were updated.
- Next Step: Commit, push, open PR for #1629, update PR metadata, then run review/merge-ready/hosted gate before merge and issue closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20 local PR3 validation passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; git diff --check; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py --surface governance-closeout; full python3 tools/check_cli_contract.py; python3 tools/host_adapter_check.py; python3 tools/check_npm_package.py; python3 tools/check_release_surface.py; node --test test/npm-package-smoke.test.mjs; python3 tools/loom.py suite evidence validate --target . --item WI-1629 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1629 --json; temporary HOME smoke tests for host install/register confirmed no target repo writes.
- Recovery Boundary: PR3 only: issue #1629. Do not implement PR4 CLI command deletion, PR5 package/gate/migration convergence, or v0.17.0 release execution in this lane.
- Current Lane: milestone-14-pr3-global-codex-plugin-install

## Runtime Evidence

- Run Entry: 2026-06-20 PR2 plugin payload implementation lane
- Logs Entry: local command output retained in current Codex milestone/14 thread
- Diagnostics Entry: PR2 carrier activated after PR1 closeout left repository in `no_active_item` idle state; plugin payload generation, package surface, and installed runtime fixtures now consume `plugins/loom/skills` rather than single-skill package metadata.
- Verification Entry: `python3 tools/skills_surface.py check`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/loom.py skills package --json`; `python3 tools/loom.py skills release-check --json`; `make py-compile`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate`; suite validate/evidence/carrier; `git diff --check`.
- Lane Entry: milestone-14-pr2-plugin-payload

## Sources

- Static Truth: .loom/work-items/WI-1629.md
- Dynamic Truth: .loom/progress/WI-1629.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
