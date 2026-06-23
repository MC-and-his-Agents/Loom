# WI-1776 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1776 is a bounded CLI behavior slice that reclassifies existing release readback evidence into a short closeout verdict and adds focused fixture coverage. It does not add publish authority, credentials, destructive cleanup, or a new release framework.
- Consumer Boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, and downstream #1778 may consume this minimal suite without treating skipped full-path artifacts as completed.
- Recheck Condition: Require full suite artifacts if this work expands into publishing, version bump automation, credential handling, destructive cleanup mutations, release workflow design, or new host API write behavior.
- Scope Proof: Changes are limited to `tools/loom.py`, `tools/check_cli_contract.py`, `docs/evidence/fixtures/release-readback-fixtures.json`, WI-1776 carriers, `.loom/specs/WI-1776`, `.loom/reviews/WI-1776*.json`, and `.loom/status/current.md`.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1776 is a bounded CLI release readback verdict slice with direct fixture coverage and no new external publish authority. consumer boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, and #1778 may consume this minimal suite without requiring skipped full-path artifacts. recheck condition: require full suite artifacts if the work expands into publishing, version bump automation, credential handling, destructive cleanup mutations, release workflow design, or new host API write behavior.

## Scenarios

- S1: published release evidence returns verdict `published` only when tag, GitHub Release, npm package, workflow success, package surface, and terminal carrier agree.
- S2: missing tag, GitHub Release, npm package, or workflow evidence returns verdict `missing` with short next action.
- S3: release evidence bound to a different target commit or dist-tag returns verdict `drifted`.
- S4: failed release workflow, unreadable readback surface, package surface mismatch, or same-head main-worktree-busy merge fallback returns verdict `blocked`.
- S5: `release resume` remains non-mutating and exposes the same diagnostic contract plus resume metadata.
- S6: no-release judgment remains `no_release` and does not infer publish intent from VERSION.

## Acceptance

- [x] A1: `release readback` and `release resume` expose verdict, diagnostic, and next_action fields.
- [x] A2: fixture coverage includes `published`, `missing-tag`, `npm-missing`, `drifted-tag`, `blocked-workflow`, and `multi-worktree-main-busy`.
- [x] A3: release readback combines package surface and carrier terminal state with tag, GitHub Release, npm, and workflow readbacks.
- [x] A4: same-head main-worktree-busy fallback reports a blocked verdict with host merge API next action.
- [x] A5: no-release judgment remains non-publishing and non-mutating.
- [x] A6: `release-readback` contract, Python compile, JSON fixture validation, live dry-run readback, and `git diff --check` pass.
