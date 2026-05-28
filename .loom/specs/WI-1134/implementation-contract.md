# WI-1134 Implementation Contract

## Authority Boundary

- `suite_gate_validation` is gate input evidence only.
- It must not replace Work Item truth, recovery truth, review records, merge-ready results, closeout evidence, or docs/source truth.
- Suite validation commands remain read-only and must not write host state, Project state, review records, merge-ready results, closeout comments, or generated skills.

## Required Behavior

- Pre-review and implementation review flow expose `suite-evidence-validate` and `suite-carrier-validate` steps.
- Merge-ready consumes the same suite gate payload before host merge checks.
- Implementation review `allow` records fail closed when suite evidence/carrier validation is `block` or `fallback`.
- Successful implementation review records include consumed suite validation commands and evidence/task-carrier locators.

## Non-goals

- No closeout semantic change.
- No consistency-analysis implementation.
- No spec-kit command names or `.specify/` layout.
- No reverse changes to frozen #1014-#1020 contracts.
