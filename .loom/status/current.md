# Current Status

## Derived Fact Chain View

- Item ID: WI-1294
- Goal: Publish the #1217/#1227 metadata-only adoption CLI and skills changes through a follow-up Loom CLI release.
- Scope: WI-1294 owns the minimal release follow-up for issue #1294: bump root `VERSION` to `v0.13.10`, bump root `package.json` to `0.13.10`, regenerate `skills/*/loom-package.json` `repo_version` surfaces, mark the stale WI-1217 progress carrier terminal after #1217 closeout, keep metadata-only behavior unchanged, verify release/version/package/CLI contracts, merge a follow-up PR, verify `loom-cli-release` publishes `v0.13.10` tag/GitHub Release/npm package, and record final release evidence back on #1217. Ownership includes `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/work-items/WI-1294.md`, `.loom/progress/WI-1294.md`, `.loom/progress/WI-1217.md`, `.loom/specs/WI-1294/*`, `.loom/specs/WI-1294/implementation-contract.md`, `.loom/reviews/WI-1294*.json`, `VERSION`, `package.json`, and generated `skills/*/loom-package.json` files. Ownership excludes metadata-only adoption behavior changes, installer release reactivation, package rename, unrelated governance cleanup, or rewriting #1217 implementation evidence.
- Execution Path: issue #1294 -> branch work/1294-release-followup -> PR -> CI -> merge -> main `loom-cli-release` publish verification -> #1217/#1294 closeout evidence.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1294.md
- Review Entry: .loom/reviews/WI-1294.json
- Validation Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/check_cli_contract.py; npm pack --dry-run --json --ignore-scripts; python3 tools/skills_surface.py check; python3 tools/loom.py skills check --target . --json; git diff --check; PR/CI; main `loom-cli-release`; npm/tag/release smoke.
- Closing Condition: PR is merged, `v0.13.10` tag and GitHub Release point at the follow-up merge commit, `@mc-and-his-agents/loom@0.13.10` is published on npm, #1217 has corrected final release evidence, and #1294 is closed.
- Current Checkpoint: pre-review
- Current Stop: Follow-up issue #1294 is open; branch `work/1294-release-followup` is active; #1217 has a correction comment recording that #1227 post-merge release failed closed because `v0.13.9` was already published on a different commit; local pre-PR validation for the v0.13.10 release bump has passed.
- Next Step: Commit and push the v0.13.10 release bump, open the follow-up PR, validate CI, merge after green, then verify tag/GitHub Release/npm publication.
- Blockers: None recorded.
- Latest Validation Summary: Initial evidence: #1227 post-merge `loom-cli-release` push run https://github.com/MC-and-his-Agents/Loom/actions/runs/26888581620 failed closed with `AUTO_PUBLISH_ALLOWED=true` because tag `v0.13.9` points to `18036d7b9555ca4ecf7e007b747a7f3ab0d77edd`, while #1227 merged at `442778ca1f47426a850c4f39bf06b6a1e750700b`. Local v0.13.10 pre-PR evidence passed: `python3 tools/check_release_surface.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`; `python3 tools/check_cli_contract.py`; `python3 tools/skills_surface.py check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json`; `npm pack --dry-run --json --ignore-scripts` produced `mc-and-his-agents-loom-0.13.10.tgz`; `git diff --check`; and shared scripts pycache check found no `skills/shared/scripts` or `src/skills/shared/scripts` `__pycache__`. Post-merge evidence remains pending and must be added after merge: main `loom-cli-release`, `v0.13.10` tag, GitHub Release, npm package, #1217 final comment, and #1294 closeout.
- Recovery Boundary: Do not change metadata-only adoption semantics, do not reactivate installer release, do not overwrite existing tags/releases/npm versions, and do not rewrite #1217 implementation evidence.
- Current Lane: release-followup

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: release/version/package/CLI checks
- Lane Entry: release-followup

## Sources

- Static Truth: .loom/work-items/WI-1294.md
- Dynamic Truth: .loom/progress/WI-1294.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
