# WI-847 Implementation Contract

## Owned Files

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `skills/*/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/*/.loom-runtime/shared/scripts/loom_check.py`
- `docs/methodology/harness/pr-merge-gate.md`
- `.loom/work-items/WI-847.md`
- `.loom/progress/WI-847.md`
- `.loom/specs/WI-847/*`
- `.loom/reviews/WI-847*.json`

## Required Behavior

- The implementation approval consumer must reject `spec_review` as an implementation approval kind.
- PR gate output must expose the non-approval evidence boundary without turning lint evidence into a second authored truth source.
- The new `governance_lint` section must use `loom-governance-lint-status/v1` and embed `loom-governance-lint-result/v1` result envelopes.
- Negative fixtures must fail closed for raw-only evidence and spec-review-kind bypass attempts.

## Boundaries

- Review record schema remains unchanged.
- Raw/shadow/runtime evidence remains evidence-only.
- No repo-specific guardian name, CI job, review path, or downstream architecture rule becomes a Loom core default.
