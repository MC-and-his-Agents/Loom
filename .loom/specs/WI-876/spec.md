# WI-876 Spec

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md, evidence-map.md, consistency-analysis.md, execution-breakdown.md, task-carrier.md; rationale: #876 is a contract-only documentation Work Item that freezes PR metadata machine carrier boundaries and generated reference sync without changing parser/runtime behavior; consumer boundary: #877 parser preflight, #874 render/edit validation, #875 fixtures, and #957 readiness guard must not treat skipped artifacts as completed; recheck condition: switch to full suite if this Work Item starts changing parser behavior, CLI outputs, review gates, host actions, or runtime contracts.

## Acceptance

- Repo companion contract declares stable machine carrier fields: `schema_version`, `carrier_id`, `surface`, `repo_specific_field_set`, `authority_locator`, `applicability_locator`, `enforcement`, `parser_version`, and `source_range_or_hash`.
- PR template guidance separates human-readable PR body sections from machine-readable metadata carriers.
- Machine carrier guidance states parser/CLI output does not replace Work Item, review, merge-ready, closeout, or docs/source truth.
- Generated skills references remain synchronized with source references.

## Non-Goals

- Do not implement #877 parser behavior changes.
- Do not implement #874 render/edit post-write validation.
- Do not add #875 Markdown drift or legacy migration fixtures.
- Do not implement #957 pre-review readiness/cost guard.
