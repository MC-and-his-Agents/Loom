# WI-1127 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1127 is a narrow CLI slice for evidence-map inspect/validate and only needs spec, plan, implementation contract, evidence-map, docs, and CLI contract fixtures; consumer boundary: carrier, merge-ready, closeout, consistency-analysis, E2E governance, and evidence-map scaffold consumers remain owned by later Work Items under #1126/#1136/#1145; recheck condition: this change expands beyond evidence-map inspect/validate or a later consumer requires the full suite path.

## Goal

Evidence-map consumers can inspect rows and block stale, missing, or incomplete evidence before later merge-ready automation consumes that state.

## Key Scenarios

### Scenario S1

Given a Work Item with an authored evidence-map
When `loom suite evidence inspect` runs
Then the CLI reports the evidence-map locator, row count, normalized rows, freshness vocabulary, and consumed contracts without mutating the repo.

### Scenario S2

Given evidence rows for behavior evidence, test evidence, and fresh verification input
When `loom suite evidence validate` runs
Then validation passes only when the fresh verification input consumes present behavior and test evidence rows.

### Scenario S3

Given a missing evidence-map, stale evidence row, incomplete row, or missing fresh verification binding
When `loom suite evidence validate` runs
Then validation blocks with structured findings and stable failure kinds.

## Acceptance Criteria

- [ ] A1: `loom help --json` declares `suite evidence inspect` and `suite evidence validate` as implemented suite commands.
- [ ] A2: `suite evidence inspect` is read-only and reports evidence-map locator, rows, required evidence types, freshness values, consumed contracts, and inspect-only gaps.
- [ ] A3: `suite evidence validate` is read-only and passes for behavior/test/fresh verification happy evidence.
- [ ] A4: `suite evidence validate` blocks missing evidence-map, stale/conflicting evidence, incomplete required row fields, and fresh verification rows that do not consume present behavior and test evidence.
- [ ] A5: CLI contract fixtures cover happy, missing, and stale evidence cases.
