# WI-1785 Spec

## Suite Path Decision

- Suite path: minimal
- Rationale: WI-1785 is a narrow hosted workflow compatibility fix. It only passes the PR metadata surface already declared in the PR body into the existing `pr-gate` checker.
- Consumer Boundary: suite validate, implementation review, PR metadata, hosted checks, PR gate, controlled merge, and #1784/#1778 may consume this minimal suite without treating skipped full-path artifacts as completed.
- Recheck Condition: Require full suite artifacts if this work expands into a new PR metadata schema, new gate framework, release workflow design, or broader CI orchestration changes.
- Scope Proof: Changes are limited to `.github/workflows/pr-merge-gate.yml`, WI-1785 carriers, `.loom/specs/WI-1785`, `.loom/reviews/WI-1785*.json`, and `.loom/status/current.md`.
- Review Requirement: current_head_review_required
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: bounded CI glue fix with direct local and hosted validation; consumer boundary: hosted gate and closeout PR merge readiness; recheck condition: expand if metadata schema or gate framework changes.

## Scenarios

- S1: A PR body with `loom:repo-pr-metadata` surface `closeout` makes hosted `loom-pr-merge-gate` call `pr-gate check --surface closeout`.
- S2: A PR body without a closeout metadata surface keeps hosted `loom-pr-merge-gate` on `merge_ready`.
- S3: Malformed or absent metadata does not crash the workflow and falls back to `merge_ready`.

## Acceptance

- [x] A1: Closeout PR metadata is consumed as closeout surface by the hosted gate.
- [x] A2: Ordinary merge-ready PR metadata remains merge_ready.
- [x] A3: Malformed metadata fallback remains merge_ready and lets the existing gate report the parser error.
- [ ] A4: #1784 hosted `loom-pr-merge-gate` passes after this fix is merged and #1784 branch consumes it.
