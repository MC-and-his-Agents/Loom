# WI-1538 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1538 is a carrier-only terminal checkpoint sync for already-completed WI-1531 host facts; formal suite artifacts would duplicate the retained closeout evidence without adding behavior, runtime, or contract coverage. consumer boundary: this skips only formal suite artifacts; fact-chain, shadow parity, PR metadata/readback, current-head review for WI-1538, hosted checks, PR gate, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if scope expands into runtime behavior, closeout profile semantics, hosted gate behavior, downstream implementation, release mechanics, security/privacy, migration, or external-visible behavior. scope proof: `git diff origin/main...HEAD` must stay limited to WI-1538 carriers/spec stub, WI-1531 terminal progress checkpoint fields, active status surface, and derived shadow hashes. review requirement: current-head review must verify this is carrier-only and does not rewrite WI-1531 retained implementation review history.

## Objective

Synchronize WI-1531 terminal checkpoint carrier so completed host facts no longer appear as live same-workspace drift during later Work Item purity checks.

## Acceptance Scenarios

### S1: WI-1531 terminal checkpoint is explicit

Given WI-1531 already has terminal closeout metadata, its dynamic progress checkpoint states `closed_out` and its next step is terminal.

### S2: Retained implementation review history is preserved

Given WI-1531 closeout checks consume the original implementation review validation summary, WI-1538 does not rewrite that summary or backdate review evidence.

### S3: Downstream purity can proceed

Given a later Work Item runs build/review checks in the same workspace, WI-1531 is not reported as host-complete carrier drift requiring another closeout sync.

## Non-Goals

- No runtime behavior changes.
- No hosted gate, PR gate, closeout profile, or release/no-release changes.
- No downstream #1532/#1533/#1534 implementation.
- No rewrite of WI-1531 retained implementation review history.
