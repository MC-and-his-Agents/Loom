# WI-1554 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1554 is a bounded CLI wrapper/runtime parameter contract hardening with deterministic contract coverage and no hosted admission, release, carrier closeout, or one-shot post-merge closeout behavior; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue tracking, and milestone closeout consumers may use this minimal suite plus Work Item evidence for merge wrapper and closeout wrapper argument contracts; recheck condition: require full suite artifacts if scope expands into hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, security/privacy behavior, external host writes, or #1555 closeout run orchestration.

## Objective

Make `tools/loom.py` expose high-risk merge and closeout command parameters that match the shared runtime contract, fail early for the old merge placeholder literal `pr`, and keep wrapper/runtime drift covered by focused CLI contract checks.

## Acceptance Scenarios

### S1: Merge wrapper forwards the numeric PR

Given an operator invokes `loom merge check 1288`, the wrapper delegates to the controlled merge runtime with `--pr 1288`.

### S2: Merge wrapper does not leak the placeholder

Given an operator invokes `loom merge check pr`, the wrapper fails during argument parsing with `argument pr-number: invalid int value: 'pr'` instead of forwarding `--pr pr`.

### S3: Existing merge options remain preserved

Given an operator passes `--work-item`, `--head-sha`, and `--merge-method`, the wrapper preserves those values when delegating to the runtime.

### S4: Closeout wrapper forwards runtime-supported parameters

Given an operator invokes `loom closeout --item WI-1554 --issue 1554 --pr 1562 --branch work/1554-wrapper-closeout-contract`, the wrapper delegates to `closeout check` with the same Work Item, host object, branch, payload fixture, gate profile, and readback options supported by the runtime.

### S5: Gate closeout remains a closeout check facade

Given an operator invokes `loom gate closeout --item WI-1554 --issue 1554`, the wrapper delegates to the runtime `closeout check` path and preserves the argument values without adding host writes.

## Non-Goals

- Do not implement retained Work Item parsing or closeout item lookup; #1494 owns that behavior and is already consumed as runtime surface.
- Do not implement #1555 one-shot post-merge closeout run.
- Do not change hosted admission, classifier taxonomy, closeout freeze profile semantics, release behavior, closeout gate semantics, or external host writes.
