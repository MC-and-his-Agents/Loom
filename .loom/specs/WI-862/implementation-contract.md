# WI-862 Implementation Contract

## Allowed Change Surface

- Story intake governance, review, goal, gate, Work Item, and template documents.
- `src/skills/loom-story/**`
- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_init.py`
- `src/skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/loom_story_carriers.py`
- Generated `skills/**` surfaces derived from `src/skills`.
- `examples/new-project/.loom/**` runtime and scaffold refreshes.
- Loom Work Item, progress, spec, review, and status carriers for `WI-862`.

## Required Properties

- Story Business Confirmation must remain separate from User Story, Story Readiness, Work Item, spec, plan, recovery, review, merge-ready, and closeout state.
- Confirmation must be limited to business semantics and must not request technical approval from the user.
- `revision-requested` must return to story shaping before spec / plan consumption.
- `not-applicable` must remain available for pure governance, maintenance, formatting, link repair, and carrier-only work.
- Runtime contract summaries and story carrier checks must expose and enforce the confirmation states.

## Exit Criteria

- PR is bound to `WI-862` and #862.
- Local and GitHub validation pass.
- PR merges to `main` through controlled merge.
- #862 is closed after closeout state is synchronized.
