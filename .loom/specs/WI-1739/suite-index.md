# WI-1739 Suite Index

## Scope

WI-1739 wires the `loom ship --apply` main path so safe repairable metadata, carrier, and shadow drift are handled before merge gates consume PR metadata or review state.

## Suite Artifacts

- Spec: .loom/specs/WI-1739/spec.md
- Plan: .loom/specs/WI-1739/plan.md
- Implementation Contract: .loom/specs/WI-1739/implementation-contract.md
- Research: .loom/specs/WI-1739/research.md
- Contracts: .loom/specs/WI-1739/contracts.md
- Readiness Checklist: .loom/specs/WI-1739/readiness-checklist.md
- Evidence Map: .loom/specs/WI-1739/evidence-map.md
- Consistency Analysis: .loom/specs/WI-1739/consistency-analysis.md
- Execution Breakdown: .loom/specs/WI-1739/execution-breakdown.md
- Task Carrier: .loom/specs/WI-1739/task-carrier.md

## Suite Path Decision

- Suite path: full
- Rationale: `loom ship --apply` orchestrates mutating delivery behavior and must keep pre-merge gate order explicit.
