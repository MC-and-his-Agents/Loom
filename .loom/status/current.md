# Current Status

## Derived Fact Chain View

- Item ID: WI-1719
- Goal: Deprecate single SKILL distribution version semantics in the legacy installer so per-skill metadata is contract-only and cannot drive freshness or upgrade recommendations.
- Scope: Update `packages/loom-installer` payload skill metadata, single-skill version context, version context comparison, and installer regression tests; author WI-1719 minimal suite, evidence, task carrier, progress, status, and bootstrap fact-chain binding. Non-goals: no current single SKILL install recommendation, no legacy installer recommendation, no full-repo clone fallback, no CLI release/version bump, no npm publish, no release files, no host command boundary docs/skills, no `tools/check_npm_package.py`, no `test/plugin_payload_hash_test.py`, and no other worktree changes.
- Execution Path: issue #1719 -> worktree `/Users/mc/dev/Loom-WI-1719-skill-contract-version-only` -> branch `work/1719-skill-contract-version-only` -> PR #1725 -> merge -> issue closeout.
- Workspace Entry: `./WI-1719/..`
- Recovery Entry: `.loom/progress/WI-1719.md`
- Review Entry: `.loom/reviews/WI-1719.json`
- Validation Entry: `npm --prefix packages/loom-installer test`; `npm --prefix packages/loom-installer run check:docs`; `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`; `git diff --check`; `python3 tools/loom.py fact-chain --target . --item WI-1719 --json`; `python3 tools/loom.py suite validate --target . --item WI-1719 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1719 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1719 --json`.
- Closing Condition: PR #1725 is merged into `main`, issue #1719 is closed, and closeout consumes the PR, issue, branch, and main readback.
- Current Checkpoint: merge checkpoint
- Current Stop: PR #1725 is open; local gate and merge-ready passed at head `7d825708cb2a16e8b75d139a37a0caf28256255d`; hosted merge gate exposed that `Workspace Entry` must be repo-local, and local purity requires an item-scoped entry distinct from historical `.` carriers.
- Next Step: Commit the item-scoped repo-relative workspace-entry carrier repair, rebind spec/code review to the new head, refresh PR #1725 metadata, then rerun PR gate, merge-ready, and hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation passed in `/Users/mc/dev/Loom-WI-1719-skill-contract-version-only` after installer package metadata patch bump `0.1.148` -> `0.1.149`: `npm --prefix packages/loom-installer test` passed 22 installer tests after rebuilding payload and compiling TypeScript; `npm --prefix packages/loom-installer run check:docs` passed; `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main` passed with `0.1.148 -> 0.1.149`; `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --item WI-1719 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1719 --json` passed; `python3 tools/loom.py suite evidence validate --target . --item WI-1719 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1719 --json` passed.
- Recovery Boundary: WI-1719 owns only `packages/loom-installer/**`, directly related installer tests/docs, `.loom/work-items/WI-1719.md`, `.loom/progress/WI-1719.md`, `.loom/progress/WI-1719-build-evidence.json`, `.loom/specs/WI-1719/**`, `.loom/status/current.md`, and `.loom/bootstrap/init-result.json`. It must not touch `tools/check_npm_package.py`, `test/plugin_payload_hash_test.py`, host command boundary README/skills docs, root release version files, npm publish/release files, installer tags/releases, other worktrees, #1714, or #1720.
- Current Lane: skill-contract-version-only

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1719 build started in the issue-scoped worktree for branch `work/1719-skill-contract-version-only`.
- Logs Entry: Local validation output retained in this Codex thread and summarized in `.loom/progress/WI-1719.md`.
- Diagnostics Entry: legacy `skill_package_version` may be tolerated in installed metadata for migration diagnostics but is not emitted in current single-skill version context and is ignored for freshness comparison.
- Verification Entry: targeted installer tests and docs sync passed before final carrier validation; final validation is recorded in `.loom/progress/WI-1719.md`.
- Lane Entry: skill-contract-version-only

## Sources

- Static Truth: `.loom/work-items/WI-1719.md`
- Dynamic Truth: `.loom/progress/WI-1719.md`
- Locator Truth: `.loom/bootstrap/init-result.json`
- Fact Chain CLI: `python3 .loom/bin/loom_init.py fact-chain --target .`
