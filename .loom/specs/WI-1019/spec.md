# WI-1019 Spec

## Goal

Connect full spec suite consumption into the review / merge-ready gate chain.

## Scope

In scope:

- Pre-review and review consumption of full suite locators, evidence-map and consistency-analysis.
- Merge checkpoint and merge-ready fail-closed semantics for blocking consistency gap, stale evidence and head drift.
- Closeout reconciliation consumption of evidence-map, consistency-analysis, merge commit, target branch and issue state.
- Minimal path `not_applicable` rationale semantics.
- #1020 integration requirements as follow-up evidence.

Out of scope:

- Redefining #1016 full/minimal suite.
- Redefining #1017 task carrier.
- Redefining #1018 evidence-map or consistency-analysis.
- Implementing CLI surface.
- Modifying skills routing or generated skills runtime surface.

## Scenarios

### S1: Pre-review Exposes Blocking Gaps

Given a Work Item chooses full spec path
When pre-review evaluates suite, evidence-map and consistency-analysis inputs
Then blocking suite, evidence or consistency gaps are exposed before formal review.

### S2: Review Consumes Inputs Without Becoming Second Truth

Given pre-review has exposed gate-chain inputs
When formal review records its conclusion
Then the review record can backlink consumed full suite, evidence-map and consistency-analysis locators without replacing authored review truth.

### S3: Merge-Ready Fails Closed

Given review has passed
When merge-ready sees blocking consistency gap, stale evidence or head drift
Then merge-ready fails closed instead of using CI or host checks as a substitute.

### S4: Closeout Reconciles Merged Result

Given a PR has merged
When closeout checks Work Item, PR, merge commit, target branch, issue state, evidence-map and reconciliation audit
Then merged does not equal closed_out unless all required backlinks are consistent.

### S5: Minimal Path Is Explicit

Given a Work Item uses minimal path
When a gate consumes missing full path artifacts
Then the gate can accept only explicit `not_applicable` rationale with source locator, consumer boundary and recheck condition.

## Acceptance Criteria

- AC1: Gate-chain docs define full suite inputs without redefining full suite.
- AC2: Review docs state pre-review exposes blocking gap before formal review.
- AC3: Merge checkpoint docs fail closed on blocking consistency gap, stale evidence and head drift.
- AC4: Closeout docs require evidence-map / consistency-analysis / reconciliation backlinks before closed_out.
- AC5: Minimal path `not_applicable` is distinguished from missing and deferred.
- AC6: #1020 receives skills/GitHub profile/generated-surface integration requirements.
