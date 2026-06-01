# WI-874 Spec

- Suite path: minimal
- Full suite artifacts not_applicable: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: #874 is a narrow render/edit validation slice on the existing #876/#877 metadata carrier and parser contract; consumer boundary: #875 and #957 must consume this as render/edit readiness only, not completed drift fixture expansion or cost guard behavior; recheck condition: switch to full suite if this Work Item starts changing frozen core contracts, closeout semantics, host merge execution, or #1107 suite CLI structure.

## Acceptance

- `pr-metadata preflight` can validate a rendered PR body artifact without requiring a live PR number.
- Post-edit/readback validation can compare rendered and read-back PR body machine block hashes while allowing human Markdown sections to move or change.
- Machine block drift after `gh pr edit` fails closed with structured `body_artifact` evidence and fallback guidance.
- PR template and methodology docs recommend `gh pr edit --body-file` plus readback preflight instead of shell command substitution.
- Body artifact preflight proves carrier readability only; it does not replace Work Item, review, merge-ready, closeout, or docs/source truth.

## Non-Goals

- Do not expand #875 Markdown drift / legacy migration fixture coverage beyond focused render/edit hash comparison.
- Do not implement #957 pre-review readiness or cost guard.
- Do not expand into #1107 full spec suite CLI tree.
