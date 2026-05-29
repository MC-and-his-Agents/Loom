# WI-1150 Spec

## Suite Contract

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md; rationale: #1150 is a negative governance fixture Work Item that proves stale evidence and host conflict blocks without needing full-path design artifacts; consumer boundary: source-self fixture validation, implementation review, PR evidence, merge-ready handoff, and #1145 progress may consume the fixture evidence but must not treat skipped full-path artifacts as completed; recheck condition: switch to full suite if #1150 starts authoring product design, API contracts, readiness checklist, or consistency-analysis behavior.

## Scenarios

### Scenario S1

Given evidence rows bound to a stale HEAD, stale PR head, or stale validation summary
When source-self and installed `loom_check` fixture validation runs
Then `suite evidence validate` blocks with `stale_evidence` taxonomy and remediation.

### Scenario S2

Given task carrier rows where Project Done, checklist checked, PR merged, and issue open host signals conflict
When source-self and installed `loom_check` fixture validation runs
Then `suite carrier validate` blocks with `carrier_truth_conflict` taxonomy and remediation.

## Acceptance Criteria

- AC-1: The fixture asserts stale HEAD, PR head, and validation summary binding cannot be consumed as merge-ready or closeout evidence.
- AC-2: The fixture asserts Project / issue / checklist / PR carrier conflicts block before merge-ready consumption.
- AC-3: The fixture checks machine-readable taxonomy and remediation, not just command exit status.
- AC-4: Generated skills runtime surfaces are synchronized after source fixture changes.
- AC-5: Production reconciliation behavior is not changed.

## Non-Goals

- Do not close #1150 or advance parent #1145 / #1107 closeout.
- Do not alter #1149 or #1151-#1153 carriers.
- Do not copy spec-kit `/speckit.*` command names or `.specify/` layout.
