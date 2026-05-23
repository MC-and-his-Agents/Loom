# Current Status

## Derived Fact Chain View

- Item ID: WI-963
- Goal: 定义 `loom_check` 并发隔离与运行现场纯度合同，作为 #962 P0-A 后续实现事项的权威依据。
- Scope: `loom_check` source/consumer profile 边界、run id、同 worktree single-flight、同仓多 worktree 并行、跨仓临时目录隔离、默认 subprocess 宿主环境净化、stable fixture 默认不重写、Node installer regression 写入隔离、shared references 与 source self-check 合同锚点，分发面同步所需的 installer 版本元数据，以及将已合并 WI-859 carrier 标记为 terminal 以解除 #963 merge gate 的历史活跃现场冲突；不实现 #964/#965/#966/#967/#968 的具体机制，不扩大到 #866/#873/#969/#953 或 CLI-first 主线。
- Execution Path: checks/loom-check-runtime-purity-contract
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-963.md
- Review Entry: .loom/reviews/WI-963.json
- Validation Entry: git diff --check; py_compile_clean for loom_check scripts; skills_surface check; installer version bump check; npm test --prefix packages/loom-installer; tools/loom_check.py --profile source .
- Closing Condition: PR #976 merged or merge-ready with #963 closed by PR, branch/head/PR/check state aligned, and #962 can consume the contract as closeout basis for later P0-A work.
- Current Checkpoint: merge
- Current Stop: PR #976 is open for `work/963-loom-check-purity-contract` at reviewed implementation head `53cb31fb0fbc23e1c49139fd1ce91edae7954dc2`; the runtime-purity contract, shared references, generated skills surface, Work Item carrier, and formal spec suite are present.
- Next Step: Consume PR #976 checks and merge gate; if all required checks pass, merge #976 and allow #963 to close before starting #964/#967.
- Blockers: None recorded.
- Latest Validation Summary: Passed for WI-963: git diff --check; python3 tools/py_compile_clean.py tools/loom_check.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py; python3 tools/skills_surface.py check; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main -> OK, 0.1.134 -> 0.1.135; npm test --prefix packages/loom-installer -> 21 pass; python3 tools/loom_check.py --profile source . -> loom_check: OK, profile source, checked 40 source/distribution surfaces; host-binding inspect for #962/#963/PR #976/branch work/963-loom-check-purity-contract/head f8da5f93fa825db7e8c098a24b3bc5ed9cd7e802 returned pass; pr-gate check for PR #976/head f8da5f93fa825db7e8c098a24b3bc5ed9cd7e802 returned pass.
- Recovery Boundary: Scope is #963 contract only: `loom_check` runtime purity docs, shared references, generated surface sync, source self-check anchors, installer version metadata required by distribution gate, WI-963 PR gate carriers, and terminal marking for merged WI-859 to remove stale active-carrier conflict. Excludes #964/#965/#966/#967/#968 implementation and excludes #866/#873/#969/#953/CLI-first work.
- Current Lane: merge-ready-gate-consumption

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-963.md
- Dynamic Truth: .loom/progress/WI-963.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
