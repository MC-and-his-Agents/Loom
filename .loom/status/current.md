# Current Status

## Derived Fact Chain View

- Item ID: WI-1721
- Goal: Define and implement Codex plugin source, marketplace source, and runtime cache readback so Loom can tell whether the current Codex plugin payload is fresh.
- Scope: Issue #1721 only. Update `tools/loom.py`, focused CLI contract checks, and WI-1721 carriers. Non-goals: no repo-local plugin install surface, no single SKILL install, no v0.19.0 release.
- Execution Path: issue #1721 -> branch `work/1721-codex-source-cache-readback` -> worktree `.loom/..` -> targeted validation -> PR -> controlled merge -> closeout.
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1721.md
- Review Entry: .loom/reviews/WI-1721.json
- Validation Entry: `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `python3 -m py_compile tools/loom.py tools/check_cli_contract.py`; `git diff --check`; `python3 tools/loom.py fact-chain --target . --item WI-1721 --json`.
- Closing Condition: PR for `work/1721-codex-source-cache-readback` is merged into `main`, issue #1721 is closed, and closeout consumes PR, issue, hosted checks, target branch, and repo carrier readback.
- Current Checkpoint: merge
- Current Stop: PR #1748 is ready for merge gate evaluation at head c7f08859ce7f7781ecbbd2b17c943164f773b2a2 after hosted PR body readback matched local metadata and authored review was consumed.
- Next Step: Run PR gate, hosted checks, controlled merge, and closeout for WI-1721.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local validation on branch `work/1721-codex-source-cache-readback`: `python3 tools/check_cli_contract.py --surface adoption-host-metadata` passed after adding current/stale/metadata-missing/malformed-manifest fixtures; `python3 -m py_compile tools/loom.py tools/check_cli_contract.py` passed; `git diff --check` passed; `python3 tools/loom.py suite validate --target . --item WI-1721 --json` passed; `python3 tools/loom.py suite evidence validate --target . --item WI-1721 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1721 --json` passed; `python3 tools/loom.py fact-chain --target . --item WI-1721 --json` passed. `loom host doctor --host codex --scope user --json` now reports `plugin_payload_readback` with source-payload, marketplace-source, runtime-cache layers and actionable freshness state.
- Recovery Boundary: WI-1721 owns Codex plugin source/marketplace/runtime readback in host doctor and focused contract tests. It does not implement version/doctor aggregate freshness for #1715, stale refresh UX for #1716, broad fixtures for #1717, or v0.19.0 release closeout for #1718.
- Current Lane: codex-source-cache-readback

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1721 build started in issue-scoped worktree `work/1721-codex-source-cache-readback`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1721.md`.
- Diagnostics Entry: `loom host doctor --host codex --scope user --json` reports Codex plugin payload source, marketplace source, and runtime cache readback.
- Verification Entry: Targeted CLI contract, py_compile, and diff checks passed before suite validation.
- Lane Entry: codex-source-cache-readback

## Sources

- Static Truth: .loom/work-items/WI-1721.md
- Dynamic Truth: .loom/progress/WI-1721.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
