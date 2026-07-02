# Current Status

## Derived Fact Chain View

- Item ID: WI-1892
- Goal: 文档化 marketplace 安装 plugin、npm 安装 CLI、每仓 repo adoption 独立校验的安装边界。
- Scope: 仅限 #1892：同步 README 安装/升级说明、docs/adoption/global-cli-user-plugin-contract.md、docs/adoption/host-adapter-matrix.md，以及必要 WI-1892 suite/carrier；不实现 workstation registry/global cache/upgrade orchestrator/legacy migration，不修改 CLI/runtime/plugin payload。
- Execution Path: issue #1892 -> branch work/1892-install-boundary-docs -> PR -> review/merge-ready/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1892.md
- Review Entry: .loom/reviews/WI-1892.json
- Validation Entry: rg -n "marketplace|host install|npm install -g|repo adoption|metadata-only" README.md docs/adoption/global-cli-user-plugin-contract.md docs/adoption/host-adapter-matrix.md; python3 tools/loom.py suite validate --target . --item WI-1892 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1892 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1892 --json; python3 tools/loom.py fact-chain --target . --item WI-1892 --json; git diff --check
- Closing Condition: Install-boundary docs are merged, #1892 is closed, and Loom closeout consumes PR/review/validation/merge evidence.
- Current Checkpoint: build
- Current Stop: PR #1918 is at head f5031c21; install-boundary docs, release-doc-contract wording, WI-1891 terminal carrier sync, and WI-1892 spec/implementation review artifacts are recorded.
- Next Step: Run build/merge checkpoints, PR gate, hosted checks, merge-ready, controlled merge, and closeout for #1892.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-02T19:15Z local pass after hosted-failure fix: check_release_surface.py --surface release-doc-contract, targeted rg boundary search, suite validate, suite evidence validate, suite carrier validate, fact-chain, and git diff --check.
- Recovery Boundary: WI-1892 docs-only scope remains README, docs/adoption/global-cli-user-plugin-contract.md, docs/adoption/host-adapter-matrix.md, WI-1892 carriers/reviews; no CLI/runtime/plugin payload changes.
- Current Lane: docs-boundary

## Runtime Evidence

- Run Entry: 2026-07-03 WI-1890 work is active in `/Users/mc/dev/Loom` on branch `work/1890-marketplace-catalog-contract`.
- Logs Entry: checker/docs/generated metadata implementation authored and locally validated; no external runtime or marketplace installation action has been executed in this WI.
- Diagnostics Entry: prior WI-1884 runtime evidence drift was corrected; #1890 now records fresh suite/evidence/carrier/fact-chain and focused checker/package validation.
- Verification Entry: 2026-07-03T01:05+08:00 validation passed on head `0b296f1bb2f681e77851a38b72a0ce2ad71fc606` for suite evidence, suite carrier, fact-chain, and git diff --check after repo-relative workspace entry refresh. Earlier implementation validation on head `2e1b0ac33c84900c19e444e59a131a01ab4b5e54` passed py_compile_clean, demo fixture drift and aggregate, runtime-copy-parity, plugin-payload-hash, suite validate/evidence/carrier, fact-chain, local PR gate, and git diff --check.
- Lane Entry: checker-contract

## Sources

- Static Truth: .loom/work-items/WI-1892.md
- Dynamic Truth: .loom/progress/WI-1892.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
