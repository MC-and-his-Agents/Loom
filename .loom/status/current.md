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
- Current Checkpoint: closed
- Current Stop: Follow-up PR #1295 merged at `04c2ed43493f348e6039f938ad9bc7948bb1e3dd`; `loom-cli-release` main push run https://github.com/MC-and-his-Agents/Loom/actions/runs/26893658462 succeeded; `v0.13.10` tag and GitHub Release point at the merge commit; `@mc-and-his-agents/loom@0.13.10` is published on npm; #1217 received corrected final release evidence; #1294 is closed.
- Next Step: None for WI-1294; release follow-up closeout is complete.
- Blockers: None.
- Latest Validation Summary: Final release evidence: PR #1295 merged at `04c2ed43493f348e6039f938ad9bc7948bb1e3dd`; `loom-cli-release` main push run https://github.com/MC-and-his-Agents/Loom/actions/runs/26893658462 succeeded; release workflow checks included release surface, version surface, CLI contract, npm package contract, npm dry-run, tag creation, npm publish, and GitHub Release creation; git tag `v0.13.10` resolves to `04c2ed43493f348e6039f938ad9bc7948bb1e3dd`; GitHub Release https://github.com/MC-and-his-Agents/Loom/releases/tag/v0.13.10 was published as `Loom CLI v0.13.10`; npm `@mc-and-his-agents/loom@0.13.10` is published; target branch validation on `main` after merge passed for `VERSION=v0.13.10`, `package.json=0.13.10`, `tools/check_release_surface.py`, `tools/version_surface_check.py`, `tools/check_npm_package.py`, `tools/skills_surface.py check`, `tools/loom.py skills check --target . --json`, `tools/loom.py fact-chain --target . --json`, and `git diff --check`; #1217 received corrected final release evidence; #1294 is closed.
- Recovery Boundary: Do not change metadata-only adoption semantics, do not reactivate installer release, do not overwrite existing tags/releases/npm versions, and do not rewrite #1217 implementation evidence.
- Current Lane: terminal

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: release/version/package/CLI checks
- Lane Entry: terminal

## Sources

- Static Truth: .loom/work-items/WI-1294.md
- Dynamic Truth: .loom/progress/WI-1294.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
