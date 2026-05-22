# WI-847 Spec

## Outcome

Governance Lint exposes and enforces the authored review approval boundary so raw review output, shadow/runtime review evidence, PR body text, CI success, and GitHub review comments cannot satisfy semantic approval.

## Acceptance

- `pr-gate check` keeps `work_item.review_entry` as the only semantic approval truth.
- `approval_boundary` explicitly marks raw, shadow, runtime, PR body, CI, and GitHub review comment evidence as non-approval sources.
- `pr-gate check` emits a `governance_lint` section for the approval boundary with taxonomy, provenance, bindings, surface, and fallback.
- `checkpoint merge` and `pr-gate check` reject `spec_review` records as implementation approval.
- Raw-only evidence and spec-review-kind fixtures fail closed and keep the approval bypass taxonomy visible.
- Advisory or derived lint output does not author a review verdict or replace the review record.

## Non Goals

- Do not run semantic review.
- Do not replace `pr merge gate` or `controlled merge`.
- Do not change the review record schema.
- Do not add repo-specific lint rules or hardcoded downstream repository policy to Loom core.
