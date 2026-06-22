# Current Status

## Derived Fact Chain View

- Item ID: WI-1719
- Goal: Deprecate single SKILL distribution version semantics in the legacy installer so per-skill metadata is contract-only and cannot drive freshness or upgrade recommendations.
- Scope: Update `packages/loom-installer` payload skill metadata, single-skill version context, version context comparison, and installer regression tests; author WI-1719 minimal suite, evidence, task carrier, progress, status, and bootstrap fact-chain binding. Non-goals: no current single SKILL install recommendation, no legacy installer recommendation, no full-repo clone fallback, no CLI release/version bump, no npm publish, no release files, no host command boundary docs/skills, no `tools/check_npm_package.py`, no `test/plugin_payload_hash_test.py`, and no other worktree changes.
- Execution Path: issue #1719 -> worktree `/Users/mc/dev/Loom-WI-1719-skill-contract-version-only` -> branch `work/1719-skill-contract-version-only` -> commit and push; PR creation is not part of this request.
- Workspace Entry: `/Users/mc/dev/Loom-WI-1719-skill-contract-version-only`
- Recovery Entry: `.loom/progress/WI-1719.md`
- Review Entry: not required until PR/review is requested.
- Validation Entry: `npm --prefix packages/loom-installer test`; `npm --prefix packages/loom-installer run check:docs`; `git diff --check`; `python3 tools/loom.py fact-chain --target . --item WI-1719 --json`; `python3 tools/loom.py suite validate --target . --item WI-1719 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1719 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1719 --json`.
- Closing Condition: branch is pushed with tests/checks passing and no forbidden ownership touched; issue/PR closeout is reserved for the main thread.
- Current Checkpoint: pushed branch checkpoint
- Current Stop: Installer code/test changes and WI-1719 minimal suite carriers are committed and pushed on branch `work/1719-skill-contract-version-only`.
- Next Step: Main thread may open a PR or continue #1719 review/merge-ready when ready; this worker does not create a PR.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation passed in `/Users/mc/dev/Loom-WI-1719-skill-contract-version-only`: `npm --prefix packages/loom-installer ci` installed missing devDependencies with no vulnerabilities; `npm --prefix packages/loom-installer test` passed 22 installer tests after rebuilding payload and compiling TypeScript; `npm --prefix packages/loom-installer run check:docs` passed; `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --item WI-1719 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1719 --json` passed; `python3 tools/loom.py suite evidence validate --target . --item WI-1719 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1719 --json` passed. Post-commit carrier sync was validated with fact-chain, suite validate/evidence/carrier, and diff hygiene before amend/push readback.
- Recovery Boundary: WI-1719 owns only `packages/loom-installer/**`, directly related installer tests/docs, `.loom/work-items/WI-1719.md`, `.loom/progress/WI-1719.md`, `.loom/progress/WI-1719-build-evidence.json`, `.loom/specs/WI-1719/**`, `.loom/status/current.md`, and `.loom/bootstrap/init-result.json`. It must not touch `tools/check_npm_package.py`, `test/plugin_payload_hash_test.py`, host command boundary README/skills docs, release version files, npm publish/release files, other worktrees, #1714, or #1720.
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
