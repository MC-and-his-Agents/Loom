# Current Status

## Derived Fact Chain View

- Item ID: WI-1712
- Goal: Define the authoritative plugin payload version and hash contract for #1711 so later implementation work can decide Codex plugin freshness without confusing plugin surface compatibility, skills registry versions, or single-skill contract versions.
- Scope: Update version authority and install-surface contracts; mirror the skills distribution contract into `src/skills`, `skills`, and `plugins/loom/skills`; add a `version_surface_check` guard for the new terminology. Ownership: WI-1712 owns only the listed contract docs, generated skill mirrors, version surface checker guard, not_applicable suite decision, task carrier, and fact-chain carriers. Non-goals: no CLI behavior change, no payload hash implementation, no plugin metadata generation, no legacy installer behavior change, no version bump, and no release publication in this Work Item.
- Execution Path: issue #1712 -> branch `work/1712-payload-version-contract` -> worktree `/Users/mc/dev/Loom-WI-1712-payload-version-contract` -> PR #1723 -> merge -> issue closeout.
- Workspace Entry: `/Users/mc/dev/Loom-WI-1712-payload-version-contract`
- Recovery Entry: `.loom/progress/WI-1712.md`
- Review Entry: `.loom/reviews/WI-1712.json`
- Validation Entry: `python3 tools/version_surface_check.py`; `python3 tools/skills_surface.py check`; `git diff --check`; `python3 tools/check_release_surface.py --surface release-doc-contract`; `python3 tools/check_release_surface.py --surface forbidden-release-surface-patterns`; `python3 tools/check_npm_package.py --surface npm-package-manifest`.
- Closing Condition: PR #1723 is merged into `main`, issue #1712 is closed, and #1713-#1722 can consume the frozen payload version/hash contract.
- Current Checkpoint: build checkpoint
- Current Stop: PR #1723 is open at head `ae67f7cb6a8928752ba085afec65019da2f4752d`; contract files, generated skill mirrors, and `version_surface_check` guard are committed and pushed.
- Next Step: Consume PR metadata readback, hosted checks, semantic review, and merge-ready gate for PR #1723.
- Blockers: Awaiting hosted checks and review/merge-ready evidence.
- Latest Validation Summary: 2026-06-22 local validation passed on head `ae67f7cb6a8928752ba085afec65019da2f4752d`: `python3 tools/version_surface_check.py`; `python3 tools/skills_surface.py check`; `git diff --check`; `python3 tools/check_release_surface.py --surface release-doc-contract`; `python3 tools/check_release_surface.py --surface forbidden-release-surface-patterns`; `python3 tools/check_npm_package.py --surface npm-package-manifest`. PR metadata render, preflight, and readback passed for PR #1723 with `governance_intensity=light`, `change_class=docs_governance`, `suite_path=not_applicable`, and `release_judgment=no_release`.
- Recovery Boundary: WI-1712 owns only the contract freeze and its fact-chain carriers. It does not implement payload hashing, metadata generation, host source/cache readback, stale plugin diagnostics, legacy installer retirement, fixtures, version bump, npm publish, GitHub release, or #1711 final release closeout.
- Current Lane: payload-version-contract

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1712 contract freeze started in issue-scoped worktree `/Users/mc/dev/Loom-WI-1712-payload-version-contract`.
- Logs Entry: Local validation output retained in this Codex thread and summarized in `.loom/progress/WI-1712.md`.
- Diagnostics Entry: `plugin_payload_version` follows the root Loom release/npm package; `plugin_payload_hash` is the payload freshness authority; `plugin_surface_version`, `registry_version`, `contract_version`, and legacy `skill_package_version` are separate lines.
- Verification Entry: 2026-06-22 local validation and PR metadata preflight/readback passed for PR #1723 head `ae67f7cb6a8928752ba085afec65019da2f4752d`.
- Lane Entry: payload-version-contract

## Sources

- Static Truth: `.loom/work-items/WI-1712.md`
- Dynamic Truth: `.loom/progress/WI-1712.md`
- Locator Truth: `.loom/bootstrap/init-result.json`
- Fact Chain CLI: `python3 .loom/bin/loom_init.py fact-chain --target .`
