# WI-1029 Plan

## Implementation Target

Update the story intake authority contract and contract-summary runtime so story readiness can be consumed consistently by #1015 and downstream #1030-#1032 work.

## Steps

1. Update `docs/methodology/governance/story-intake.md` and shared references with the new verdict vocabulary and Business Confirmation boundary.
2. Add a templates-layer `story-intake.md` entry that points to the governance contract instead of duplicating it.
3. Update `loom_flow.py`, `loom_check.py`, and `loom_story_carriers.py` in source and installed surfaces to use the new vocabulary.
4. Update `loom-story` output contract references so generated runtime surfaces can consume the same vocabulary.
5. Regenerate the checked-in skills surface.
6. Validate with focused searches, `git diff --check`, `tools/skills_surface.py check`, and `loom_check` contract-only.

## Constraints

- Do not modify #1030 user-story scaffold fields in this WI.
- Do not modify #1031 `loom-story` routing instructions in this WI.
- Do not redefine full/minimal spec suite, task carrier, consistency analysis, gate-chain, or CLI automation.
- Keep #1012 open.

## Validation

- `git diff --check`
- focused `rg` for readiness and business confirmation vocabulary
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Entry Conditions

- #1014 is closed and Project Done.
- #1015 is open and owns story intake.
- #1029 is the active Work Item branch/worktree.
