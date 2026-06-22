# Current Status

## Derived Fact Chain View

- Item ID: WI-1732
- Goal: Retire legacy `@mc-and-his-agents/loom-installer` as a tombstone package so it no longer maintains active plugin, single-skill, upgrade, or verify installer behavior.
- Scope: Issue #1732 only. Update `packages/loom-installer/**`, node-installer CI/release gates, release-surface guard, and WI-1732 carriers. Non-goals: no `npm deprecate` execution, no root Loom v0.19.0 release, no #1715/#1716/#1717/#1721 implementation, and no restoration of single-skill or legacy plugin install surfaces.
- Execution Path: issue #1732 -> branch `work/1732-retire-loom-installer-package` -> worktree `.loom/..` -> targeted validation -> PR -> controlled merge -> closeout.
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1732.md
- Review Entry: .loom/reviews/WI-1732.json
- Validation Entry: `npm --prefix packages/loom-installer run check:release`; `node packages/loom-installer/scripts/run-regression.mjs`; `python3 tools/check_loom_check_runtime_regressions.py --surface installer-regression-lock-output`; `python3 tools/check_release_surface.py --surface installer-sunset-guard`; `python3 tools/skills_surface.py check --surface generated-tree-drift`; `python3 tools/py_compile_clean.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/loom_check.py`; `git diff --check`; `python3 tools/loom.py suite validate --target . --item WI-1732 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1732 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1732 --json`; `python3 tools/loom.py fact-chain --target . --item WI-1732 --json`.
- Closing Condition: PR for `work/1732-retire-loom-installer-package` is merged into `main`, issue #1732 is closed, and closeout consumes PR, issue, hosted checks, target branch, and repo carrier readback.
- Current Checkpoint: merge
- Current Stop: PR #1733 is ready for merge-gate and hosted-check consumption at head `51ba53c808b024a6aba4869ff601824952cf2202`.
- Next Step: Wait for required hosted checks and rerun PR merge gate before controlled merge.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation on branch `work/1732-retire-loom-installer-package`: `npm --prefix packages/loom-installer run check:release` passed; `node packages/loom-installer/scripts/run-regression.mjs` passed; `python3 tools/check_loom_check_runtime_regressions.py --surface installer-regression-lock-output` passed; `python3 tools/check_release_surface.py --surface installer-sunset-guard` passed; `python3 tools/skills_surface.py check --surface generated-tree-drift` passed; `python3 tools/py_compile_clean.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py plugins/loom/skills/shared/scripts/loom_check.py` passed; direct `check_root_self_plugin_install(Path('.'))` returned pass; `git diff --check` passed; `python3 tools/loom.py suite validate --target . --item WI-1732 --json` passed; `python3 tools/loom.py suite evidence validate --target . --item WI-1732 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1732 --json` passed; `python3 tools/loom.py fact-chain --target . --item WI-1732 --json` passed; `python3 tools/loom_flow.py adopt verify --target . --item WI-1732` passed; `python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking` passed; `python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .` passed; `python3 tools/loom.py pr metadata-readback 1733 --surface merge_ready --json` passed for head `51ba53c808b024a6aba4869ff601824952cf2202`.
- Recovery Boundary: WI-1732 owns tombstoning the deprecated `@mc-and-his-agents/loom-installer` package and removing active installer behavior tests / bump gates. It does not execute `npm deprecate`, publish v0.19.0, or implement plugin freshness diagnostics outside the installer tombstone boundary.
- Current Lane: installer-tombstone

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1732 build continued in issue-scoped worktree `work/1732-retire-loom-installer-package`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1732.md`.
- Diagnostics Entry: `@mc-and-his-agents/loom-installer` now emits only a fail-closed tombstone result with migration commands.
- Verification Entry: Targeted tombstone checks and Loom suite / evidence / carrier / fact-chain checks passed after carrier refresh.
- Lane Entry: installer-tombstone

## Sources

- Static Truth: .loom/work-items/WI-1732.md
- Dynamic Truth: .loom/progress/WI-1732.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
