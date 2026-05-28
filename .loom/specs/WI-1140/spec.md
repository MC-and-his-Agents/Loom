# WI-1140 Spec

- Suite path: minimal

- Full suite artifacts not_applicable: rationale: #1140 is a narrow scenario skill integration slice that consumes existing suite CLI JSON and does not add new suite artifact types or consistency analysis; consumer boundary: closeout reconciliation, consistency analyze, and E2E governance fixtures remain later Work Items under #1136/#1145; recheck condition: scenario skills start writing suite truth, bypass CLI JSON, or replace Work Item/review/merge-ready/closeout/docs truth.

## Goal

Scenario skills consume canonical full spec suite CLI JSON instead of reimplementing suite readiness rules.

## Scope

- In scope: `loom-build`, `loom-spec-review`, `loom-pre-review`, `loom-review`, and `loom-merge-ready` CLI JSON consumption boundaries; story/resume/handoff locator-only boundaries; source/generated skill sync; docs and CLI contract checks.
- Out of scope: new suite command names, consistency analyze implementation, GitHub reconciliation, closeout automation, host writes, new issue-tree nodes, `/speckit.*`, and `.specify/`.

## Key Scenarios

### Scenario S1

Given a Work Item with authored suite artifacts
When `loom build --json` runs
Then build consumes `loom suite validate --json` and `loom suite carrier validate --json` before reporting build readiness.

### Scenario S2

Given formal spec review
When `loom flow spec-review` or `loom gate spec-review` runs
Then spec review consumes `loom suite validate --json` and fails closed if CLI JSON is unavailable or blocking.

### Scenario S3

Given pre-review, implementation review, or merge-ready
When the scenario gate runs
Then the gate consumes `loom suite evidence validate --json` and `loom suite carrier validate --json` as gate input evidence.

### Scenario S4

Given an installed skill runtime without readable suite CLI JSON
When suite readiness is required
Then the skill fails closed instead of falling back to embedded suite readiness rules.

## Acceptance Criteria

- A1: Build output exposes `suite_validation` and `suite_carrier_validation` consumed from repo-local CLI JSON.
- A2: Spec-review no longer falls back to embedded formal suite presence checks when CLI JSON is unavailable.
- A3: Pre-review/review/merge-ready continue exposing `suite_gate_validation` as gate input evidence only.
- A4: Scenario skill docs and route matrix state that CLI JSON is the machine interface while skills remain agent-facing entrances.
- A5: Source/generated skills and `.loom/bin` runtime stay synchronized.
- A6: CLI output does not replace Work Item, review record, merge-ready result, closeout evidence, Project status, docs, or source truth.
- A7: The implementation does not introduce `/speckit.*` or `.specify/` surfaces.
