# WI-1540 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1540 is a carrier-only closeout sync that consumes already-completed WI-1538 host facts; formal suite artifacts would duplicate terminal evidence without adding behavior, runtime, or contract coverage. consumer boundary: this skips only formal suite artifacts; fact-chain, shadow parity, PR metadata/readback, current-head review for WI-1540, PR gate, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if scope expands into runtime behavior, closeout profile semantics, hosted gate behavior, downstream implementation, release mechanics, security/privacy, migration, or external-visible behavior. scope proof: `git diff origin/main...HEAD` must stay limited to WI-1540 carriers/spec stub, WI-1538 terminal progress checkpoint fields, active status surface, and derived shadow hashes. review requirement: current-head review must verify this is carrier-only and does not rewrite WI-1538 or WI-1531 retained review history.

## Objective

Consume WI-1538 terminal closeout facts into repo-local Loom carriers so later Work Item purity checks do not treat WI-1538 as a live same-workspace drift source.

## Acceptance Scenarios

### S1: WI-1538 terminal facts are explicit

Given PR #1537 merged and issue #1538 was closed, WI-1538 progress records `closed_out` terminal facts with PR, merge commit, target branch, issue close time, and evidence locator.

### S2: Closeout sync has its own current-head review

Given PR #1539 performs the closeout sync, WI-1540 owns the active fact-chain, recovery, and review carriers for the current PR head.

### S3: Downstream purity can proceed

Given a later Work Item runs build/review checks in the same workspace, WI-1538 is not reported as an active carrier drift requiring another closeout sync.

## Non-Goals

- No runtime behavior changes.
- No hosted gate, PR gate, closeout profile, or release/no-release changes.
- No downstream #1529, #1532, #1533, or #1534 implementation.
- No rewrite of WI-1538 or WI-1531 retained review history.
