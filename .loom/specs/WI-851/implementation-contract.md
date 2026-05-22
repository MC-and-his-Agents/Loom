# WI-851 Implementation Contract

## Owned Files

- `docs/evidence/fixtures/governance-lint-negative-fixtures.json`
- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `skills/*/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/*/.loom-runtime/shared/scripts/loom_check.py`
- `packages/loom-installer/package.json`
- `packages/loom-installer/package-lock.json`
- `.loom/work-items/WI-851.md`
- `.loom/progress/WI-851.md`
- `.loom/specs/WI-851/*`
- `.loom/reviews/WI-851*.json`

## Required Behavior

- Negative fixtures must be synthetic, versioned, and machine-consumed by repo-local checks.
- Approval bypass fixtures must keep `work_item.review_entry` as the only semantic approval source.
- PR body text, CI success, raw/runtime review evidence, and `spec_review` records must not satisfy implementation approval.
- Stale review/head drift evidence must fail closed instead of being consumed as fresh approval.
- PR gate Governance Lint must emit an `evidence_stale` blocking result when authored approval exists but no longer binds to the current head or validation summary.
- Companion and interop fixtures must validate locator/truth boundaries without creating new authored truth carriers.
- Hardcoding guard fixtures must keep downstream guardian/review path examples confined to evidence or explicit prohibition contexts.

## Boundaries

- No standalone `loom lint` command.
- No repo-specific guardian implementation copied into Loom.
- No new authored truth source for lint verdicts.
