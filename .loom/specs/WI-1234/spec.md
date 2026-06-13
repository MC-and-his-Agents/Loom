# WI-1234 Spec

## Suite Decision

- Suite path: not_applicable
- Suite-level not_applicable: rationale: WI-1234 is a focused retained item lookup runtime change with direct focused test coverage instead of a formal suite artifact set; consumer boundary: suite validate, spec review, pr-gate, merge-ready, and closeout may consume this only as formal suite non-applicability and must still require Work Item truth, current-head review, PR metadata, hosted checks, release/no-release judgment, controlled merge, and closeout evidence; recheck condition: lookup scope expands beyond retained Work Item discovery or generated/runtime/bootstrap sync changes.

## Scope Proof

- Implementation surface: retained Work Item lookup for closeout and reconciliation paths.
- Positive coverage: canonical `WI-<issue>`, historical `GH-21-LOOM-UPGRADE-BASELINE`, associated artifact evidence, and recovery entry evidence.
- Negative coverage: ambiguous retained carriers fail closed with explicit diagnostics.
- Exclusions: #1232, #1233, #1235, #1236, #1237, #1296, Round 10, Round 11, Deferred roadmap, release, merge, guardian, controlled merge, and shared contract/schema/failure vocabulary changes.
