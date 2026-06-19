# Current Status

## Derived Fact Chain View

- Item ID: WI-1601
- Goal: Add release readback and resume classification.
- Scope: Issue #1601 only: add release intent/readback/resume classification for tag, GitHub Release, npm, and workflow state including partial publish cases; do not replace GitHub Actions publishing and do not perform v0.15.0 release closeout.
- Execution Path: issue #1601 -> branch work/1601-release-resume -> PR #1606 -> merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1601.md
- Review Entry: .loom/reviews/WI-1601.json
- Validation Entry: workspace audit; py_compile_clean; check_cli_contract --surface release-readback; release surface checks; PR metadata readback/preflight; hosted loom-check
- Closing Condition: Issue #1601 and PR #1606 are terminal only after release resume behavior, fact-chain, spec review, implementation review, hosted checks, target branch, release/no-release evidence, and closeout evidence are consistent.
- Current Checkpoint: merge checkpoint
- Current Stop: Release readback/resume implementation and suite carriers are ready for review.
- Next Step: Commit carriers, record spec and implementation reviews, update PR body, and rerun merge-ready checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-19: suite validate passed; suite evidence validate passed; suite carrier validate passed; workspace audit passed after carrier refresh; release-readback CLI contract passed; release-doc-contract check passed; git diff --check passed.
- Recovery Boundary: Scope remains issue #1601 release readback/resume classification only; no v0.15.0 publishing, GitHub Actions replacement, closeout role, dependency parser, host auth, or PR metadata changes.
- Current Lane: release resume lane

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1515 v0.14.2 release-required closeout preparation
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: #1515 is release_required because #1554/#1555 shipped CLI/runtime behavior after v0.14.1; v0.14.2 release PR merge remains publish-capable and requires explicit user approval before merge.
- Verification Entry: pre-merge release validation passed for the WI-1515 v0.14.2 release payload and PR #1591 metadata: version/release/npm/package/skills/CLI contract/suite/fact-chain/audit/build/review/shadow checks passed; PR metadata render/readback/preflight passed; post-merge release evidence remains pending.
- Lane Entry: milestone-12-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1601.md
- Dynamic Truth: .loom/progress/WI-1601.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
