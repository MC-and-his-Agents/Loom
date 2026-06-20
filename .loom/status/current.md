# Current Status

## Derived Fact Chain View

- Item ID: WI-1633
- Goal: 完成 milestone #14 PR4：删除 repo-local plugin、skills 与 runtime 写入路径，并清理 root `loom` CLI command matrix、安装参数与 single-skill 命令面。
- Scope: issue #1633 和 #1639；允许修改 root CLI host/skills surface、CLI contract 测试、命令矩阵文档、README/adoption docs、本 Work Item carrier、PR3 terminal carrier sync、shadow status evidence refresh 和必要 PR metadata。Ownership constraints: main executor owns `tools/loom.py`, `tools/check_cli_contract.py`, command/adoption docs, `.loom/work-items/WI-1633.md`, `.loom/progress/WI-1633*.json`, `.loom/progress/WI-1633.md`, `.loom/progress/WI-1629.md` terminal sync, `.loom/specs/WI-1633/*`, `.loom/status/current.md`, `.loom/bootstrap/init-result.json` fact-chain locator sync, `.loom/shadow/merge-ready-loom.json`, and `.loom/shadow/closeout-loom.json` for this PR only；不修改 npm package 载荷实现、legacy residue gate、迁移长文档、v0.17.0 发布或 release closeout。
- Execution Path: issues #1633/#1639 -> branch work/1633-1639-cli-surface-cleanup -> PR4 -> targeted CLI contract checks -> hosted gate -> merge -> issues closeout。
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1633.md
- Review Entry: .loom/reviews/WI-1633.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; git diff --check; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/host_adapter_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; node packages/loom-installer/scripts/check-doc-sync.mjs
- Closing Condition: PR4 merges into main, issues #1633/#1639 close against the merged PR, and closeout check consumes PR/head/check evidence without starting PR5.
- Current Checkpoint: build checkpoint
- Current Stop: PR4 implementation, local validation, suite evidence/carrier validation, build evidence, review record, PR metadata preflight, and shadow parity refresh are complete; hosted gate rerun, merge, and issue closeout are still pending.
- Next Step: Push shadow refresh, mark PR #1652 ready, then wait for hosted gate.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20 local PR4 validation passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; git diff --check; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/host_adapter_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; node packages/loom-installer/scripts/check-doc-sync.mjs; python3 tools/loom.py suite evidence validate --target . --item WI-1633 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1633 --json; python3 tools/loom.py build --target . --item WI-1633 --build-evidence .loom/progress/WI-1633-build-evidence.json --json passed with attempt WI-1633-build-6d9edf541d1a-0ed65ec4be16; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking passed after shadow status hash refresh.
- Recovery Boundary: PR4 only: issues #1633/#1639. Do not implement PR5 package/verify/gate/migration convergence or v0.17.0 release execution in this lane.
- Current Lane: milestone-14-pr4-cli-surface-cleanup

## Runtime Evidence

- Run Entry: 2026-06-20 PR4 CLI surface cleanup lane
- Logs Entry: local command output retained in current Codex milestone/14 thread
- Diagnostics Entry: PR4 carrier activated after PR3 closeout; root `loom` CLI no longer exposes repo-local host install modes, `--skill-id`, or `skills sync`.
- Verification Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `git diff --check`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `node packages/loom-installer/scripts/check-doc-sync.mjs`; suite evidence/carrier validation.
- Lane Entry: milestone-14-pr4-cli-surface-cleanup

## Sources

- Static Truth: .loom/work-items/WI-1633.md
- Dynamic Truth: .loom/progress/WI-1633.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
