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
- Current Stop: Plugin payload hash repair is committed locally and local release-surface checks pass; refresh review, PR metadata, and hosted checks before controlled merge.
- Next Step: Record current-head review, refresh shadow evidence, push, update PR metadata, and rerun hosted checks for PR #1733.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation on branch `work/1732-retire-loom-installer-package`: `python3 tools/check_npm_package.py --surface plugin-payload-hash` passed with hash `60758c9e526c935dddf8512993944d4e5ca0c53f233bd74089e773c9c107db4d`; `python3 tools/check_npm_package.py` passed; `python3 tools/loom.py skills release-check --json` passed; `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --item WI-1732 --json` passed. Previous WI-1732 validation remains valid: installer tombstone release check, tombstone regression, release surface guard, generated-tree drift, root self-plugin check, suite validate/evidence/carrier, adopt verify, shadow parity, bootstrap regression, PR metadata readback, local PR gate, merge checkpoint, and hosted checks except release-judgment passed before the payload hash repair.
- Recovery Boundary: WI-1732 owns tombstoning the deprecated `@mc-and-his-agents/loom-installer` package, removing active installer behavior tests / bump gates, and keeping impacted plugin payload metadata fresh. It does not execute `npm deprecate`, publish v0.19.0, or implement plugin freshness diagnostics outside the installer tombstone boundary.
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
