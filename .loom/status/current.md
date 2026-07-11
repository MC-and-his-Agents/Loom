# Current Status

## Derived Fact Chain View

- Item ID: WI-2012
- Goal: 分发 global-CLI metadata-only carrier refresh 修复，使下游 hosted gate 实际消费已合入的语义。
- Scope: Issue #2012；保留已合入的 carrier refresh 修复，仅更新 root CLI patch release 版本、package/plugin payload release metadata 和该事项 carrier；ownership constraints are limited to `VERSION`, `package.json`, `plugins/loom/.codex-plugin/plugin.json`, `.loom/work-items/WI-2012.md`, `.loom/progress/WI-2012.md`, `.loom/status/current.md`, `.loom/specs/WI-2012/**`, and scheduler-owned review/closeout artifacts. 不修改 WebEnvoy 四仓、修复语义或 hosted gate 规则。
- Execution Path: issue #2012 -> branch work/2012-cli-release-0.28.1 -> release validation -> npm/tag/release readback
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-2012.md
- Review Entry: .loom/reviews/WI-2012.json
- Validation Entry: python3 tools/version_surface_check.py; python3 tools/check_release_surface.py --surface aggregate-release-surface; python3 tools/check_npm_package.py --surface aggregate; npm pack --dry-run --json --ignore-scripts; GitHub/npm release readback.
- Closing Condition: A new patch release publishes the merged metadata-only carrier refresh repair; the matching GitHub tag, GitHub Release, npm package and downstream Harbor #246 hosted gate all read back consistently.
- Current Checkpoint: build
- Current Stop: Patch release prepared; PR, current-head review, hosted gate, merge, and published-distribution readback remain pending.
- Next Step: Create the WI-2012 release PR for v0.28.1, then verify the merged tag, GitHub Release, npm package, and Harbor PR #246 hosted gate.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-11T01:45Z on `work/2012-cli-release-0.28.1`: `python3 tools/skills_surface.py check`, `python3 tools/loom_check.py --profile source --source-surface contract-only`, `python3 tools/check_release_surface.py`, `python3 tools/version_surface_check.py`, `python3 tools/check_npm_package.py --surface aggregate`, WI-2012 metadata-only carrier refresh regression, installed-global-cli smoke, `npm pack --dry-run --json --ignore-scripts`, suite, carrier, evidence, and build validation, and `git diff --check` passed for v0.28.1. Source repair #2028 is already merged; this branch only distributes it.
- Recovery Boundary: WI-2012 patch release only. Do not change metadata-only carrier refresh behavior, WebEnvoy product code, hosted gate logic, browser runtime behavior, or any external product action.
- Current Lane: WI-2012 metadata-only carrier refresh patch release

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: not_applicable
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-2012.md
- Dynamic Truth: .loom/progress/WI-2012.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
