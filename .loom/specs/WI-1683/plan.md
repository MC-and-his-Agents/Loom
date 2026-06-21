# WI-1683 Plan

## Implementation Plan

- Replace the docs-governance-only light gate runtime rule with a generic governance intensity gate payload.
- Preserve the existing docs-governance lite gate payload as a compatibility view for old consumers and fixtures.
- Update metadata validation so light can cover bounded low-risk docs and fixture maintenance while runtime, release, external action, and mixed changes still require upgrade.
- Extend CLI contract fixtures to prove the old docs-governance path still works and the new generic gate emits effective intensity, suite path, upgrade reasons, and authority boundaries.
- Regenerate skill and plugin runtime mirrors from `src/skills`.

## Validation Plan

- `git diff --check`
- `python3 tools/skills_surface.py generate`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/loom.py suite validate --target . --item WI-1683 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1683 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1683 --json`

## Boundaries

- This plan does not implement `loom ship`.
- This plan does not implement PR backlink safe repair or concise gate diagnostics.
- This plan does not add controlled-merge post-merge closeout chaining.
- This plan does not publish v0.18.0; release closeout remains owned by #1696.
