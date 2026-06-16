# WI-1232 Implementation Contract

## Work Item

- Work Item: WI-1232
- Issue: #1232
- Branch: `work/1232-idle-read-surfaces`
- Workspace: `/Users/mc/.codex/worktrees/c98a/Loom`
- Execution entry: idle read-surface implementation with scoped WI-1232 carriers and PR #1473 metadata.

## Approved Spec

- Spec: `.loom/specs/WI-1232/spec.md`
- Plan: `.loom/specs/WI-1232/plan.md`
- Evidence map: `.loom/specs/WI-1232/evidence-map.md`
- Task carrier: `.loom/specs/WI-1232/task-carrier.md`
- Spec review entry: `.loom/reviews/WI-1232.spec.json` remains scheduler-owned and intentionally absent until the scheduler authorizes exact-head review.

## Implementation Scope

- Consume idle/no-active-item state in fact-chain inspection without treating a valid idle repository as a broken active Work Item.
- Report valid idle state from `loom status` without blocking on active-only carrier fields.
- Keep governance surface and carrier summaries from defaulting idle/no-active-item state to `INIT-0001`.
- Preserve active Work Item fail-closed behavior for current-item locator drift and stale status surfaces.
- Synchronize only the already scoped source, runtime, generated skill, demo fixture, and WI-1232 carrier surfaces needed for the #1232 idle read-surface behavior.

## Out Of Scope

- #1233 host-truth diagnostics.
- #1234 retained lookup.
- #1235 repair/apply.
- #1236 fixture expansion beyond #1232 proof.
- #1237 docs/help finalization.
- #1296 release.
- Round 10, Round 11, Deferred roadmap, shared schema/parser/failure vocabulary changes, guardian/formal/semantic review, review artifact creation, controlled merge, closeout, release, npm, VERSION, tag, GitHub Release, or live configuration mutation.

## Validation Plan

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py $(git diff --name-only origin/main...HEAD -- '*.py')`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1232 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1232 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1232 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1232`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py carrier refresh --target . --item WI-1232 --dry-run`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity validate --target .`
- PR metadata preflight/readback for PR #1473 bound to the current branch head.
- Hosted checks readback for the pushed PR head.

## Risks And Rollback

- Risk: The implementation touches runtime and generated copies, so stale generated/runtime parity would block the gate.
- Risk: This contract makes the minimal formal suite complete for gate consumption but does not replace scheduler-owned review artifacts.
- Rollback boundary: revert the WI-1232 implementation and carrier commits on `work/1232-idle-read-surfaces`; do not mutate other Round 9 units or terminal carriers.
- Recheck condition: rerun the focused validation plan after any change to read-surface behavior, synced runtime copies, WI-1232 carriers, PR metadata, or the PR head.

## Host Binding

- PR: #1473
- Base: `main` at `a1712a017d597b22a9bf08ca5fd991d78127acf8`
- Current review requirement: scheduler-owned current-head implementation review at `.loom/reviews/WI-1232.json`.
- Current spec review requirement: scheduler-owned exact-head spec review at `.loom/reviews/WI-1232.spec.json` if the scheduler decides this minimal formal suite requires a separate spec review artifact.
- Merge-ready boundary: this contract only clears the non-review formal suite completeness prerequisite; it does not approve the implementation, create review evidence, or authorize merge.
