# WI-877 Spec

- Suite path: minimal
- Full suite artifacts not_applicable: suite-index.md, research.md, contracts.md, readiness-checklist.md, consistency-analysis.md, execution-breakdown.md; rationale: #877 is a narrow parser preflight hardening slice on existing PR metadata contracts and does not introduce a new full-suite CLI tree; consumer boundary: #874, #875, and #957 must consume this as parser readiness only, not completed render/edit validation, fixture migration expansion, or cost guard behavior; recheck condition: switch to full suite if this Work Item starts changing frozen core contracts, closeout semantics, host merge execution, or #1107 suite CLI structure.

## Acceptance

- `pr-metadata preflight` supports declared machine carriers for `pre_review`, `review`, and `merge_ready`.
- `flow pre-review`, `flow review`, and `flow merge-ready` expose parser preflight evidence when `metadata_contract.fields[*].machine_carrier.preflight.required_before` declares that surface.
- Missing, malformed, missing-field, unsupported-surface, and advisory legacy bodies return structured diagnostics rather than generic missing metadata fields.
- Diagnostics expose block locator, line/range, raw excerpt hash, expected schema/parser version, source locator or source hash, missing fields, parse error, repair hint, and fallback target.
- Parser output proves carrier readability only; it does not promote repo-specific fields into Loom core or replace Work Item, review, merge-ready, closeout, or docs/source truth.

## Non-Goals

- Do not implement PR body render/edit post-write validation for #874.
- Do not expand Markdown drift or legacy migration fixtures for #875 beyond focused #877 parser fixtures.
- Do not implement pre-review readiness/cost guard for #957.
- Do not expand into #1107 full spec suite CLI tree.
