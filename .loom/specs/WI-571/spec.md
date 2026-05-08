# WI-571 Spec

## Goal

Expose approval and sandbox policy read evidence so Loom can report execution risk boundaries without implementing or mutating host permission systems.

## Acceptance Criteria

- `policy_locators` remains declaration-time and locator-only in the repo companion contract.
- The stable policy status vocabulary is `declared`, `missing`, `conflict`, and `unsafe`.
- `policy_readiness` appears in status/governance output and includes approval policy, sandbox policy, and risk summary.
- `flow review`, `flow merge-ready`, and closeout expose applicable policy readiness under repo-specific requirements.
- Missing required policy, conflicting policy, or unsafe policy blocks the owning execution surface and uses `fallback_to`.
- Optional or advisory policy risk remains advisory and does not block core status.
- Fixtures cover missing, conflict, and unsafe policy cases.
- `make check` passes with no tracked verification drift.

## Non-Goals

- Do not request approval or change sandbox settings.
- Do not bind Loom to Codex-specific policy names.
- Do not move retained host action results from interop into repo companion.
- Do not add structured event orchestration fixtures; that belongs to #576.

