# Current Status

## Derived Fact Chain View

- Item ID: WI-1232
- Goal: Teach Loom fact-chain, status, and governance read surfaces to consume idle/no-active-item state without weakening active Work Item fail-closed checks.
- Scope: Issue #1232 only: update fact-chain inspection, status reporting, governance carrier summaries, focused CLI contract fixtures, synchronized runtime copies, and WI-1232 carriers. Excludes #1233 host-truth diagnostics, #1234 retained lookup, #1235 repair/apply, #1236 fixture expansion beyond #1232 proof, #1237 docs/help finalization, #1296 release, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, controlled merge, release, npm, tag, GitHub Release, live config mutation, and shared contract/schema/failure vocabulary changes.
- Execution Path: issue #1232 -> branch `work/1232-idle-read-surfaces` -> idle read-surface implementation and focused fixtures -> local validation -> PR metadata/readback -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1232.md
- Review Entry: .loom/reviews/WI-1232.json
- Validation Entry: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py` on touched Python files; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_status.py --target .`; PR metadata preflight/readback; hosted checks readback if available.
- Closing Condition: PR for #1232 is pushed with idle fact-chain/status/governance read surfaces, active locator/stale-status fail-closed fixture coverage, scoped WI-1232 carriers, clean local validation, PR metadata aligned to the branch head, and worker stops at scheduler-owned gate.
- Current Checkpoint: build
- Current Stop: Root carrier alignment correction for PR #1473 is in progress on branch `work/1232-idle-read-surfaces`: `.loom/bootstrap/init-result.json` selects WI-1232, `.loom/status/current.md` derives WI-1232, and `.loom/reviews/WI-1232.json` remains the pending scheduler-owned review locator.
- Next Step: Commit and push the carrier alignment correction, update/read back PR #1473 metadata for the new head, read hosted checks, then stop for scheduler-owned current-head review and gate decision.
- Blockers: Scheduler-owned current-head review/gate remains pending after carrier alignment; no local #1232 idle behavior blocker is known.
- Latest Validation Summary: 2026-06-13 root carrier alignment correction consumed scheduler readback that PR #1473 head `99ae1d78123fd6e74093c59252dd2cc5e51f5d46` was failing root governance/gate because repo-local current item still pointed at WI-1451. Pre-alignment `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1232 --dry-run` blocked only on `fact-chain: current item mismatch: expected WI-1232, got WI-1451`; runtime_state and manifest-backed runtime hashes were current. The correction aligns init-result entry points to `.loom/work-items/WI-1232.md`, `.loom/progress/WI-1232.md`, and `.loom/status/current.md`, refreshes init-result runtime provenance hashes for `.loom/bin/fact_chain_support.py`, `.loom/bin/governance_surface.py`, and `.loom/bin/loom_status.py`, and preserves the already validated #1232 idle read-surface behavior/fail-closed matrix. CodeGraph MCP was unavailable because this worktree has no initialized `.codegraph/`; fallback structural local search read `render_status_surface`, `sync_status_surface`, and `update_active_entry_points` before editing.
- Recovery Boundary: Continue only #1232 idle read-surface implementation, focused fixtures, synchronized runtime copies, scoped WI-1232 carriers, root current-item/status/shadow alignment for PR #1473, PR metadata/readback, and local validation. Do not implement #1233, #1234, #1235, #1236 beyond #1232 proof, #1237, #1296, Round 10, Round 11, Deferred roadmap, high-cost guardian/formal review, semantic review, review record, controlled merge, release, npm, tag, GitHub Release, live config mutation, or shared contract/schema/failure vocabulary changes.
- Current Lane: round-9-wi-4-idle-read-surfaces

## Runtime Evidence

- Run Entry: Worker T1232 is correcting PR #1473 root carrier alignment in scheduler thread `019ebecb-4123-7600-9527-6616c5e94d84` after hosted readback showed stale WI-1451 carrier/gate inputs on head `99ae1d78123fd6e74093c59252dd2cc5e51f5d46`.
- Logs Entry: Worksite `/Users/mc/.codex/worktrees/c98a/Loom` on branch `work/1232-idle-read-surfaces`; correction scope is limited to WI-1232 current item/status/init-result carrier alignment plus any shadow refresh proven necessary by carrier dry-run.
- Diagnostics Entry: The current blocker was root carrier/review/gate input drift, not #1232 idle behavior failure; `.loom/reviews/WI-1232.json` is intentionally absent until scheduler authorizes exact-head review.
- Verification Entry: Required correction validation is `git diff --check origin/main...HEAD`, Python compile over changed Python files, `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`, `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1232 --dry-run`, PR metadata readback, and hosted checks readback before scheduler handoff.
- Lane Entry: round-9-wi-4-idle-read-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1232.md
- Dynamic Truth: .loom/progress/WI-1232.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
