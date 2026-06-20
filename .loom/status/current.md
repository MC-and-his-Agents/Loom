# Current Status

## Derived Fact Chain View

- Item ID: WI-1626-1631-1634-1635
- Goal: 完成 milestone #14 PR5：收敛 host verify 全局 provider 验证、npm package 发布面、legacy residue hard gate 和旧安装迁移说明。
- Scope: issue #1626、#1631、#1634、#1635；允许修改 root CLI host/skills/package verification behavior、CLI contract tests、npm package manifest/smoke tests、adoption/install/package docs、本 Work Item carrier、status/fact-chain locator 和必要 PR metadata。Ownership constraints: main executor owns `tools/loom.py`, `tools/check_cli_contract.py`, `tools/check_npm_package.py`, `package.json`, `test/npm-package-smoke.test.mjs`, adoption/install/package docs including `docs/adoption/README.md`, `.loom/work-items/WI-1626-1631-1634-1635.md`, `.loom/progress/WI-1626-1631-1634-1635*.json`, `.loom/progress/WI-1626-1631-1634-1635.md`, `.loom/specs/WI-1626-1631-1634-1635/*`, `.loom/status/current.md`, `.loom/bootstrap/init-result.json`, `.loom/shadow/merge-ready-loom.json`, and `.loom/shadow/closeout-loom.json` for this PR only；不修改 VERSION、release workflow execution、v0.17.0 tag/npm/GitHub Release 或 milestone final closeout。
- Execution Path: issues #1626/#1631/#1634/#1635 -> branch work/1626-1631-1634-1635-package-gate-convergence -> PR5 -> targeted CLI/package checks -> hosted gate -> merge -> issue closeout。
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1626-1631-1634-1635.md
- Review Entry: .loom/reviews/WI-1626-1631-1634-1635.json
- Validation Entry: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py; git diff --check; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py --surface aggregate; python3 tools/host_adapter_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; node --test test/npm-package-smoke.test.mjs; node packages/loom-installer/scripts/check-doc-sync.mjs
- Closing Condition: PR5 merges into main, issues #1626/#1631/#1634/#1635 close against the merged PR, and closeout check consumes PR/head/check evidence without starting #1636/#1643 release execution in this lane.
- Current Checkpoint: build checkpoint
- Current Stop: PR5 implementation, local static/package/CLI/doc validation, suite evidence/carrier validation, build evidence, implementation-head review, and shadow parity refresh are complete; PR metadata, hosted gate, merge, and issue closeout are still pending.
- Next Step: Create PR5, validate PR metadata, and wait for hosted gate.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20 local PR5 validation passed: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py`; `git diff --check`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate` passed in 440.13s; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `node --test test/npm-package-smoke.test.mjs`; `node packages/loom-installer/scripts/check-doc-sync.mjs`; `python3 tools/loom.py suite evidence validate --target . --item WI-1626-1631-1634-1635 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1626-1631-1634-1635 --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 tools/loom.py build --target . --item WI-1626-1631-1634-1635 --build-evidence .loom/progress/WI-1626-1631-1634-1635-build-evidence.json --json` passed with attempt WI-1626-1631-1634-1635-build-b56259163ed8-28be0dcf0a6e; manual semantic review recorded in `.loom/reviews/WI-1626-1631-1634-1635.json` for implementation head b5c06d29adb14d4a59eda3b1e2870a43fe822e51; `python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1626-1631-1634-1635 --write`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed after shadow status hash refresh.
- Recovery Boundary: PR5 only: issues #1626/#1631/#1634/#1635. Do not execute v0.17.0 release, create tags, publish npm, or close milestone parent issues in this lane.
- Current Lane: milestone-14-pr5-package-gate-convergence

## Runtime Evidence

- Run Entry: 2026-06-20 PR5 package/gate convergence lane
- Logs Entry: local command output retained in current Codex milestone/14 thread
- Diagnostics Entry: PR5 carrier activated after PR4 closeout; host verify, package payload, migration docs, and legacy residue hard gate are converging for release preflight.
- Verification Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/check_npm_package.py`; `git diff --check`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 tools/check_cli_contract.py --surface aggregate`; `python3 tools/host_adapter_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `node --test test/npm-package-smoke.test.mjs`; `node packages/loom-installer/scripts/check-doc-sync.mjs`; suite evidence/carrier validation.
- Lane Entry: milestone-14-pr5-package-gate-convergence

## Sources

- Static Truth: .loom/work-items/WI-1626-1631-1634-1635.md
- Dynamic Truth: .loom/progress/WI-1626-1631-1634-1635.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
