# WI-846 Implementation Contract

## Owned Files

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `skills/*/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/*/.loom-runtime/shared/scripts/loom_check.py`
- `.loom/work-items/WI-846.md`
- `.loom/progress/WI-846.md`
- `.loom/specs/WI-846/*`
- `.loom/reviews/WI-846*.json`
- `.loom/status/current.md`

## Required Behavior

- `flow pre-review` must expose `governance_lint` as derived evidence only.
- Blocking lint results must enter the deterministic pre-review missing input set and expose `fallback_to`.
- Stale derived status evidence must block at pre-review through `governance_lint` before formal review.
- Absent optional pre-review repo companion requirement surfaces must not block the positive bootstrap path.
- `loom_check.py` must verify the pre-review lint envelope and step ordering for repo-local and installed runtime paths.

## Boundaries

- No standalone `loom lint` command.
- No #852 status or merge-ready consumption changes in this Work Item.
- No repo-specific architecture lint implementation.
- No raw review output, CI status, PR body, shadow evidence, or lint result may replace authored review records.
