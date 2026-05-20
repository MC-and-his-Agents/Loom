# Current Status

## Derived Fact Chain View

- Item ID: WI-827
- Goal: 完成 Loom 中层能力聚合批次及其前置恢复链，接通 intake、dependency、host binding、Project drift、/goal 与 Governance Lint advanced，并把 PR #856 推进到 merge-ready / merge / closeout。
- Scope: #827/#829/#830/#848/#795/#796/#798/#799/#801/#802/#803/#822/#823/#824/#825/#849/#850 的 docs、skills shared references、runtime scripts、fixtures、tests、installer version surface、PR gate carrier 和 closeout evidence；父项 #797/#800/#820 写入进度与验证证据。
- Execution Path: harness/middle-capability-aggregation
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-827.md
- Review Entry: .loom/reviews/WI-827.json
- Validation Entry: py_compile; skills_surface check; host_binding inspect; resume/status smoke; host_adapter_check; version_surface_check; git diff --check; loom_check; pr-gate check; CI checks
- Closing Condition: PR #856 绑定 WI-827，host binding/dependency/Project drift/goal/governance lint hardcoding guard 全部验证通过，PR checks 绿并尽力 controlled merge；若 host 阻断则记录 owner、证据与恢复状态。
- Current Checkpoint: merge
- Current Stop: PR #856 implementation is committed; WI-827 carrier is now active, installer package version is bumped for generated skill payload changes, and local validation is being refreshed before PR gate recheck.
- Next Step: Record current-head reviews, update PR body with Loom Work Item: WI-827, run pr-gate locally, commit, push, wait for CI, then perform controlled merge and closeout if permitted.
- Blockers: External CI was previously blocked by installer version and stale WI-819 PR gate binding; both are being repaired in this branch.
- Latest Validation Summary: PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/*.py skills/shared/scripts/*.py passed; python3 tools/skills_surface.py check passed; python3 tools/version_surface_check.py passed; git diff --check passed; node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main passed with 0.1.121 -> 0.1.122.
- Recovery Boundary: Current batch covers prerequisite recovery and middle aggregation for #827/#829/#830/#848/#795/#796/#798/#799/#801/#802/#803/#822/#823/#824/#825/#849/#850; parent evidence for #797/#800/#820 is closeout work.
- Current Lane: PR #856 on branch work/827-850-middle-capability-aggregation

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-827.md
- Dynamic Truth: .loom/progress/WI-827.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
