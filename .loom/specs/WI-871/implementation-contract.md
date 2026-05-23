# WI-871 Implementation Contract

## Invariants

- The authored review record referenced by `work_item.review_entry` remains the only semantic approval truth.
- Retained gate results are consumed as prior gate result envelopes, not as a second truth source.
- `controlled-merge` always re-reads host merge-control drift surfaces before delegating to `gh pr merge`.
- `controlled-merge check` must not execute `gh pr merge`.
- Generated `skills/` surface must remain synchronized with `src/skills/`.

## Non-goals

- Do not bypass `loom-pr-merge-gate`.
- Do not make CI success or PR body text satisfy approval.
- Do not add a new host lifecycle owner or execute host actions while resolving retained locators.
