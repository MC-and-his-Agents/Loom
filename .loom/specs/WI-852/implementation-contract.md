# WI-852 Implementation Contract

## Owned Files

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_status.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/loom-merge-ready/references/output-contract.md`
- `src/skills/loom-pre-review/references/output-contract.md`
- `src/skills/shared/references/harness/status-surface.md`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_status.py`
- `skills/shared/scripts/loom_check.py`
- `skills/*/.loom-runtime/**`
- `packages/loom-installer/package.json`
- `packages/loom-installer/package-lock.json`
- `.loom/work-items/WI-852.md`
- `.loom/progress/WI-852.md`
- `.loom/specs/WI-852/*`
- `.loom/reviews/WI-852*.json`
- `.loom/status/current.md`

## Required Behavior

- Status and merge-ready must expose Governance Lint as derived evidence only.
- Blocking lint results must enter the deterministic missing input set for the corresponding surface.
- Blocking lint must not be hidden by unrelated checkpoint fallback signals.
- Advisory lint results must remain advisory and must not change a verdict.
- Status and merge-ready must consume the stable evidence envelope, not raw linter logs.
- Authored review records remain the review authority.

## Boundaries

- No second authored status, review, validation, merge, or closeout truth source.
- No repo-specific private lint logic in Loom core.
- No changes to PR merge gate, controlled merge, closeout sync, or GitHub host authority.
- No expansion to #957, #872, #953, or CLI-first work.
