# Current Status

## Derived Fact Chain View

- Item ID: WI-1596
- Goal: Execute v0.15.0 release closeout for milestone 13 and parent FR #1594.
- Scope: Issue #1596 only: read back all milestone #13 issues/PRs/merge commits/target branch/hosted checks, advance release surfaces to v0.15.0 if authorized, record release/no-release closeout evidence, consume WI-1598 terminal carrier, and close #1594 only after GitHub and repo carriers agree. Do not backfill prerequisite implementation issues or publish without explicit authorization.
- Execution Path: issue #1596 -> branch work/1596-release-closeout -> release closeout PR -> hosted checks -> controlled merge -> main-push release workflow or authorized waiver -> terminal carrier sync
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1596.md
- Review Entry: .loom/reviews/WI-1596.json
- Validation Entry: workspace audit; release readback/resume; version/release/npm/package checks; PR metadata preflight; hosted checks; release evidence readback
- Closing Condition: Milestone #13, #1594, #1596, #1598, release/tag/npm evidence, target branch, and repo carriers are terminal and mutually consistent.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-1596 release candidate PR #1612 is open at head d9c64d439db31489f390cd8e02a2d66f0b1cc338 with PR body readback/preflight passed; hosted checks are being classified before any merge action.
- Next Step: Wait for hosted checks on PR #1612, classify failures before rerun, then perform controlled merge only after explicit release publish authorization.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-19: release readback/resume for v0.15.0 passed and classified unpublished with release_required judgment; workspace audit, carrier refresh, suite validate, suite evidence validate, suite carrier validate, version surface, release surface, npm package, package tests, npm pack dry-run, CLI version, skills release-check, skills surface, skills check, git diff check, and aggregate CLI contract passed. Aggregate CLI contract passed in 405.81s. Milestone #13 host readback found #1595 closeout drift, then #1595 was closed after terminal carrier readback.
- Recovery Boundary: Issue #1596 release closeout only; version advancement and release evidence are in scope. Release PR merge and live publish remain authorization-gated merge/publish actions.
- Current Lane: Release closeout lane

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1596 v0.15.0 release-required closeout preparation
- Logs Entry: local command output retained in current Codex milestone/13 thread
- Diagnostics Entry: #1596 is release_required because milestone #13 advances Loom merge/release/closeout behavior and the root Loom CLI candidate is unpublished at v0.15.0; release PR merge remains publish-capable and requires explicit user approval before merge.
- Verification Entry: pre-merge release validation passed for the WI-1596 v0.15.0 release payload and PR #1612 metadata: version/release/npm/package/skills/CLI contract/suite/fact-chain/audit/build/review/shadow checks passed; PR metadata render/readback/preflight passed; post-merge release evidence remains pending.
- Lane Entry: milestone-13-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1596.md
- Dynamic Truth: .loom/progress/WI-1596.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
