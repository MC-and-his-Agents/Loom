# WI-863 Plan

## Steps

1. Read #746, #750, #770, #751, #771, #863, #864, review execution docs, review skills, `loom_flow.py`, and `loom_check.py`.
2. Create an issue-scoped independent worktree and bind `WI-863` fact-chain carriers to it.
3. Update Codex App host proof discovery so complete proof wins over `CODEX_CI=1`.
4. Add missing-proof diagnostics to adapter selection metadata.
5. Add focused fixtures for `CODEX_CI=1` with valid App proof and for missing proof fallback.
6. Regenerate checked-in skills surfaces from `src/skills`.
7. Validate with py_compile, skills surface check, focused selection probe, and `loom_check`.
8. Run live Codex App review proof in the real host context.
9. Author the single review record from normalized review output and prove merge-ready or review gate consumption.
10. Push PR, pass gates, perform controlled merge, sync main, and close #863/#864 with evidence.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- focused selection probe for `CODEX_CI=1` plus valid App proof
- `python3 tools/loom_check.py`
- live Codex App `review run`
- `review record`
- `flow merge-ready` or PR semantic review gate

## Cleanup

Remove this turn's `loom-check-*` temporary directories after each `loom_check` run so validation fixtures do not exhaust the system temporary volume.
