# WI-1775 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1775 is a bounded CLI behavior slice that composes existing closeout check/run and PR metadata helpers into a low-friction closeout readback/sync path. It does not need a full research/contracts suite because #1774 and #1777 already freeze the milestone direction and upstream readback dependency.
- Consumer Boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, closeout sync, and downstream #1776 may consume this minimal suite without treating skipped full-path artifacts as completed.
- Recheck Condition: Require full suite artifacts if this work expands into release verdict taxonomy, publishing, credentials, automatic cleanup mutations, multi-worktree merge fallback, or new closeout state-machine semantics.
- Scope Proof: Changes are limited to `tools/loom.py`, `tools/check_cli_contract.py`, WI-1775 carriers, `.loom/specs/WI-1775`, `.loom/reviews/WI-1775.json`, and `.loom/status/current.md`.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1775 is a bounded CLI closeout readback/sync slice with direct fixture coverage and no new external publish authority. consumer boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, closeout sync, and #1776 may consume this minimal suite without requiring skipped full-path artifacts. recheck condition: require full suite artifacts if the work expands into release verdict taxonomy, publishing, credentials, automatic cleanup mutations, multi-worktree merge fallback, or new closeout state-machine semantics.

## Scenarios

- S1: `loom closeout status` reads PR metadata, closeout readiness, and cleanup state without mutating host or repo state.
- S2: `loom closeout sync` dry-run reports the closeout repair plan and next action without claiming fixed state.
- S3: `loom closeout sync --apply` detects PR metadata head drift, applies metadata repair, readbacks the repaired metadata, then consumes closeout run.
- S4: terminal cleanup readback reports cleanup-needed for remaining issue worktree/local branch/remote branch without deleting anything.
- S5: terminal cleanup readback blocks if the local main worktree is dirty or cleanup inputs cannot be read.

## Acceptance

- [x] A1: `closeout status` and `closeout sync` are first-class command matrix entries.
- [x] A2: command output includes blocked/fixed/next_action and cleanup verdict diagnostics.
- [x] A3: status mode does not call closeout run or mutate state.
- [x] A4: sync dry-run does not claim fixed state.
- [x] A5: metadata race repair stabilizes PR metadata before closeout run under `--apply`.
- [x] A6: cleanup-needed is represented as a non-blocking terminal cleanup diagnostic.
- [x] A7: `closeout-wrapper` contract, Python compile, and `git diff --check` pass.
