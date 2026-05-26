# WI-1030 Plan

## Implementation Target

Update the scaffold layer so #1030 consumes #1029's story intake contract and emits locator fields that downstream #1031 and #1032 can consume.

## Steps

1. Update the canonical user-story scaffold under `docs/methodology/templates/scaffold/user-story.md`.
2. Update the source skills scaffold asset and regenerate the checked-in `skills/` surface.
3. Extend story carrier validation and contract-only checks so scenario locator and Business Confirmation locator drift is caught.
4. Add WI-1030 local spec, plan, implementation contract, and progress carrier.
5. Validate with focused `rg`, skills surface check, and `loom_check` contract-only.

## Constraints

- Do not change `loom-story` skill routing or prompt behavior in this WI.
- Do not update spec-suite entry gate rules in this WI.
- Do not turn story scaffold into delivery state, review, merge-ready, or closeout truth.
- Keep #1015 open until its remaining child WIs close.

## Validation

- `git diff --check`
- `rg -n "Scenario locator|Business Confirmation locator|not_applicable|formal spec / plan" docs skills src .loom`
- `rg -n "delivery handoff|review|merge-ready|closeout|formal spec / plan" docs skills src .loom`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

## Entry Conditions

- #1029 is closed and Project Done.
- #1030 is active in `work/1030-user-story-scenario-locator`.
