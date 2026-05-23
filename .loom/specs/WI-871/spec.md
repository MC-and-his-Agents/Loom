# WI-871 Spec

## Behavior Contract

`controlled-merge check|merge` accepts optional repo-relative retained `pr-gate` and `merge-gate` result locators. When both retained results are fresh, controlled merge must consume them as prior gate results and avoid re-reading full semantic review or re-deriving merge-ready approval.

## Acceptance

- Fresh retained `pr-gate` result must be `loom-pr-merge-gate/v1`, `result == pass`, and bind the same Work Item, PR number, PR head SHA, authored review approval, reviewed validation summary, and merge checkpoint.
- Fresh retained `merge-gate` result must come from `flow merge-ready` or `checkpoint merge`, be `result == pass`, and keep the merge checkpoint plus validation summary aligned with the retained `pr-gate`.
- `controlled-merge` must still re-read current PR head, required checks, branch protection / ruleset, mergeability, and merge method as `drift_readback.mode = drift-only`.
- Missing, unreadable, stale, wrong-schema, wrong-head, wrong-Work-Item, non-pass, or validation-drift retained results must block or fall back to the appropriate prior gate.
- Retained result consumption must not let raw review output, shadow evidence, PR body text, CI success, or GitHub review comments become approval truth.
