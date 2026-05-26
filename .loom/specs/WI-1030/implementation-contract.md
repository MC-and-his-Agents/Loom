# WI-1030 Implementation Contract

## Ownership

This WI owns user-story scaffold locator outputs for scenario consumption and Story Business Confirmation consumption.

## Allowed Files

- `docs/methodology/templates/scaffold/user-story.md`
- `src/skills/shared/assets/templates/scaffold/user-story.md`
- generated `skills/shared/assets/templates/scaffold/user-story.md`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/loom_story_carriers.py`
- `skills/shared/scripts/loom_story_carriers.py`
- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_flow.py`
- generated `skills/*/.loom-runtime/**` copies of the same surfaces
- `.loom/work-items/WI-1030.md`
- `.loom/progress/WI-1030.md`
- `.loom/specs/WI-1030/**`
- `.loom/reviews/WI-1030*.json`

## Forbidden Scope

- #1029 story intake authority contract redesign.
- #1031 `loom-story` skill routing changes.
- #1032 spec-suite entry rule changes.
- Task carrier, consistency analysis, gate-chain, or CLI automation changes.

## Completion Evidence

- PR merged to `main`.
- #1030 closed as completed.
- #1015 progress comment links #1030 closeout.
- #1031 and #1032 remain open and blocked only by the intended native dependency order.
