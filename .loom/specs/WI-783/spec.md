# WI-783 Spec

## Goal

Record a canonical `.loom` surfaces version-control policy for target repository adoption.

## Acceptance Criteria

- `docs/adoption/loom-surfaces-version-control.md` defines Git-visible stable carriers, runtime scratch paths, `.gitignore` discipline, verify failure guidance, and external runtime migration expectations.
- Existing adoption and install docs link to the new policy instead of duplicating the full rule.
- `src/skills/shared/references/adoption/loom-surfaces-version-control.md` mirrors the policy for installed skills and is included in `src/skills/install-layout.json`.
- Generated `skills/` surfaces are refreshed from `src/skills`.
- Validation includes `make skills-check` and `make loom-check`.

## Non-goals

- Do not implement bootstrap or verify behavior enforcement in this checkpoint; #781 and #782 own that work.
- Do not change target repository business truth ownership.
