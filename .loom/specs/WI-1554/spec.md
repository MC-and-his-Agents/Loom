# WI-1554 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1554 first slice is a bounded CLI wrapper contract fix with deterministic contract coverage and no host, release, carrier closeout, or retained Work Item lookup behavior; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue tracking, and milestone closeout consumers may use this minimal suite plus Work Item evidence for the merge wrapper PR argument slice only; recheck condition: require full suite artifacts if scope expands into closeout item binding, hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, security/privacy behavior, or external host writes.

## Objective

Make `tools/loom.py merge check/run` expose the actual numeric PR argument expected by the runtime and fail in the wrapper when an operator passes the old placeholder literal `pr`.

## Acceptance Scenarios

### S1: Merge wrapper forwards the numeric PR

Given an operator invokes `loom merge check 1288`, the wrapper delegates to the controlled merge runtime with `--pr 1288`.

### S2: Merge wrapper does not leak the placeholder

Given an operator invokes `loom merge check pr`, the wrapper fails during argument parsing with `argument pr-number: invalid int value: 'pr'` instead of forwarding `--pr pr`.

### S3: Existing merge options remain preserved

Given an operator passes `--work-item`, `--head-sha`, and `--merge-method`, the wrapper preserves those values when delegating to the runtime.

## Non-Goals

- Do not implement or change `closeout --item`, retained Work Item binding, or closeout item lookup.
- Do not change `closeout`, `gate closeout`, hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, or external host writes.
- Do not close #1554 from this PR; this is a first fix slice only.
