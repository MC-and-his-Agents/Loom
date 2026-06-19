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
- Current Checkpoint: build checkpoint
- Current Stop: WI-1596 release version surfaces, release readiness evidence, and WI-1598 terminal carrier are authored for local validation.
- Next Step: Run release/package/skills/suite validation, record current-head review, render PR metadata, and open the v0.15.0 release PR. Do not merge or publish without explicit authorization.
- Blockers: Release publish authorization is required before merging the release PR or dispatching publish=true.
- Latest Validation Summary: 2026-06-19: pre-edit release readback/resume for v0.15.0 passed and classified unpublished with release_required judgment; workspace audit passed with no blocking active carrier drift; milestone #13 host readback found #1595 closeout drift, then #1595 was closed after terminal carrier readback.
- Recovery Boundary: Issue #1596 release closeout only; version advancement and release evidence are in scope, but release PR merge and live publish require explicit authorization.
- Current Lane: Release closeout lane

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1515 v0.14.2 release-required closeout preparation
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: #1515 is release_required because #1554/#1555 shipped CLI/runtime behavior after v0.14.1; v0.14.2 release PR merge remains publish-capable and requires explicit user approval before merge.
- Verification Entry: pre-merge release validation passed for the WI-1515 v0.14.2 release payload and PR #1591 metadata: version/release/npm/package/skills/CLI contract/suite/fact-chain/audit/build/review/shadow checks passed; PR metadata render/readback/preflight passed; post-merge release evidence remains pending.
- Lane Entry: milestone-12-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1596.md
- Dynamic Truth: .loom/progress/WI-1596.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
