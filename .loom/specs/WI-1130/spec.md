# WI-1130 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1130 is a narrow CLI validation slice for evidence freshness and HEAD / PR head binding and only needs spec, plan, implementation contract, evidence-map, docs, and CLI contract fixtures; consumer boundary: carrier validation, merge-ready integration, closeout reconciliation, consistency-analysis, E2E governance, and doctor/verify integration remain owned by later Work Items under #1126/#1136/#1145; recheck condition: this change expands beyond evidence freshness/head binding validation or a later consumer requires the full suite path.

## Goal

`loom suite evidence validate` blocks stale evidence from supporting merge-ready when evidence-map rows drift from the current execution object.

## Key Scenarios

### Scenario S1

Given an evidence-map row marked `present`
When its repo-local source locator is missing
Then evidence validation blocks with `missing_source_locator`.

### Scenario S2

Given an evidence-map row marked `present`
When its `head_sha`, `reviewed_head`, or `pr_head` binding does not match the current execution head
Then evidence validation blocks with `head_or_pr_drift`.

### Scenario S3

Given an evidence-map row marked `present`
When its validation summary digest does not match the current recovery validation summary
Then evidence validation blocks as stale evidence.

## Acceptance Criteria

- A1: `suite evidence validate` remains read-only and emits the shared readiness envelope.
- A2: Present repo-local evidence with an unreadable source locator is not accepted as fresh.
- A3: Current HEAD, reviewed head, and PR head bindings declared in evidence-map rows are checked against the current execution head.
- A4: Validation summary digest bindings declared in evidence-map rows are checked against the current recovery entry.
- A5: Existing explicit `stale` / `conflict` freshness behavior and missing fresh verification behavior continue to block.
- A6: The implementation does not introduce `/speckit.*`, `.specify/`, host writes, review writes, merge-ready writes, or closeout writes.
