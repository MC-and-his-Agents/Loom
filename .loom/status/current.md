# Current Status

## Derived Fact Chain View

- Item ID: WI-1643
- Goal: 发布 v0.17.0，交付 milestone #14 纯全局安装模型破坏性变更。
- Scope: issue #1643 only；允许修改 `VERSION`、`package.json`、本 Work Item carrier、release PR metadata 和发布后 closeout evidence。发布 PR 的代码变更仅限版本号从 v0.16.0/0.16.0 更新到 v0.17.0/0.17.0。合并到 main 后由 `loom-cli-release` 自动创建 tag、GitHub Release 和 npm package。禁止在 PR 合并前手动创建 tag、GitHub Release、npm publish 或 workflow_dispatch；禁止修改 release workflow、runtime/package payload、CLI 行为、迁移文档或 milestone #14 已合并实现。
- Execution Path: issue #1643 -> branch work/1643-release-v0.17.0 -> PR #1656 -> release surface checks -> hosted gate -> merge to main -> loom-cli-release publish -> tag/GitHub Release/npm/readback -> issue closeout。
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1643.md
- Review Entry: .loom/reviews/WI-1643.json
- Validation Entry: git diff --check; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; npm run test:package; python3 tools/loom.py release readback --target . --version v0.17.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json; npm pack --dry-run --json --ignore-scripts
- Closing Condition: PR #1656 merges into main, `loom-cli-release` publishes v0.17.0, tag/GitHub Release/npm package readback passes, and #1643 closes with release evidence.
- Current Checkpoint: merge checkpoint
- Current Stop: Release PR #1656 is open for v0.17.0 with a version-only diff; local release/package validation and pre-publish readback passed, and hosted checks remain pending.
- Next Step: Update PR #1656 metadata for WI-1643, wait for hosted checks, merge to main, then read back v0.17.0 tag, GitHub Release, npm package, workflow run, and close #1643.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20 release PR validation passed: git diff --check; python3 tools/version_surface_check.py; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; npm run test:package; python3 tools/loom.py release readback --target . --version v0.17.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json classified v0.17.0 as unpublished with tag/GitHub Release/npm gaps; npm pack --dry-run --json --ignore-scripts produced @mc-and-his-agents/loom@0.17.0 with 386 files; python3 tools/loom.py suite evidence validate --target . --item WI-1643 --json passed; python3 tools/loom.py suite carrier validate --target . --item WI-1643 --json passed.
- Recovery Boundary: WI-1643 release execution only. Do not change runtime behavior, plugin/package payload, migration docs, release workflow semantics, tag/GitHub Release/npm manually before merge, or milestone parent closeout in this PR.
- Current Lane: milestone-14-release-v0.17.0

## Runtime Evidence

- Run Entry: 2026-06-20 WI-1643 v0.17.0 release lane
- Logs Entry: local command output retained in current Codex milestone/14 thread and PR #1656 checks.
- Diagnostics Entry: release_required judgment #1636 is closed; v0.17.0 tag, GitHub Release, and npm package are absent before PR #1656 merge; release PR is version-only.
- Verification Entry: `git diff --check`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `python3 tools/loom.py release readback --target . --version v0.17.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`; `npm pack --dry-run --json --ignore-scripts`; suite not_applicable validation; carrier refresh and shadow parity.
- Lane Entry: milestone-14-release-v0.17.0

## Sources

- Static Truth: .loom/work-items/WI-1643.md
- Dynamic Truth: .loom/progress/WI-1643.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
