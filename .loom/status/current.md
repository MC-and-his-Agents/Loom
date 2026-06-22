# Current Status

## Derived Fact Chain View

- Item ID: WI-1714
- Goal: Implement deterministic plugin payload hash generation and release/package validation so Loom can detect stale Codex plugin payloads without relying on registry or per-skill versions.
- Scope: Add the `plugin-payload-hash` package validation surface, compute SHA-256 over sorted `plugins/loom` relative paths and bytes, ignore `.DS_Store`, `__pycache__`, and `*.pyc`, document the release evidence label, and add focused tests. Ownership is limited to the hash surface, release-surface documentation, focused tests, WI-1714 carriers, WI-1714 review records, and the WI-1712 terminal carrier repair required to keep this workspace pure. Non-goals: no plugin manifest metadata writeback, no host source/cache readback, no `loom version` freshness report, no host command boundary changes, no legacy installer retirement, no version bump, and no v0.19.0 release.
- Execution Path: issue #1714 -> branch `work/1714-plugin-payload-hash` -> issue-scoped worktree -> PR -> merge -> issue closeout.
- Workspace Entry: .
- Recovery Entry: `.loom/progress/WI-1714.md`
- Review Entry: `.loom/reviews/WI-1714.json`
- Validation Entry: `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `python3 tools/check_release_surface.py --surface release-doc-contract`.
- Closing Condition: PR is merged into `main`, issue #1714 is closed, and downstream #1713/#1721/#1715 can consume the hash surface.
- Current Checkpoint: build checkpoint
- Current Stop: Implementation, release evidence label, unit test, package validation surface, PR #1724 metadata readback, spec review, and implementation review are present for the branch.
- Next Step: Refresh PR metadata to the final pushed head, run review/PR gates, then proceed through merge-ready and closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation passed in `/Users/mc/dev/Loom-WI-1714-plugin-payload-hash`: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `python3 tools/check_release_surface.py --surface release-doc-contract`; `python3 tools/loom.py fact-chain --target . --item WI-1714 --json`; `python3 tools/loom.py suite validate --target . --item WI-1714 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1714 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1714 --json`; `python3 tools/loom.py build --target . --item WI-1714 --build-evidence .loom/progress/WI-1714-build-evidence.json --json`; `python3 tools/skills_surface.py check`; `python3 tools/check_cli_contract.py`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/loom.py pr metadata-readback 1724 --surface merge_ready --item WI-1714 --issue 1714 --branch work/1714-plugin-payload-hash --head-sha <head> --readback-file .loom/runtime/pr/WI-1714-pr-body-readback.md --json`; `python3 tools/loom.py review record --target . --item WI-1714 --kind spec_review --decision allow --review-file .loom/reviews/WI-1714.spec.json --json`; `python3 tools/loom.py review record --target . --item WI-1714 --kind code_review --decision allow --review-file .loom/reviews/WI-1714.json --json`.
- Recovery Boundary: WI-1714 owns only plugin payload hash generation/package validation, release evidence label docs, focused tests, its fact-chain carriers, its review records, and the WI-1712 terminal carrier repair required to keep workspace purity. It does not write plugin release metadata, implement host source/cache readback, change CLI freshness reporting, alter host command boundaries, retire single-skill installer behavior, bump versions, publish npm, or close #1711.
- Current Lane: plugin-payload-hash

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1714 started in the issue-scoped worktree for branch `work/1714-plugin-payload-hash`.
- Logs Entry: Local validation output retained in this Codex thread and summarized in `.loom/progress/WI-1714.md`.
- Diagnostics Entry: `plugin_payload_hash` is generated from sorted relative paths and bytes under `plugins/loom`; `.DS_Store`, `__pycache__`, and `*.pyc` are ignored.
- Verification Entry: 2026-06-22 local validation passed for the current WI-1714 worktree; PR metadata preflight/readback must be refreshed after each push.
- Lane Entry: plugin-payload-hash

## Sources

- Static Truth: `.loom/work-items/WI-1714.md`
- Dynamic Truth: `.loom/progress/WI-1714.md`
- Locator Truth: `.loom/bootstrap/init-result.json`
- Fact Chain CLI: `python3 .loom/bin/loom_init.py fact-chain --target .`
