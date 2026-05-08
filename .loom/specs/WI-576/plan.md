# WI-576 Plan

## Steps

1. Add the structured event evidence contract and connect it to harness/status/host action docs.
2. Add `loom_check` event evidence validation for required fields, result vocabulary, provenance, and forbidden authored truth fields.
3. Add fake agent fixtures for success, failure, and tool failure.
4. Add fake tracker fixtures for active, closed, and drift states.
5. Regenerate installed skill references and runtime script copies.
6. Bump installer payload version when generated payload behavior changes.
7. Run targeted checks and `make check`.
8. Record review evidence, open the #576 PR, merge, verify main, and close #577-#580 through the batch PR.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `npm run check:payload --prefix packages/loom-installer`
- `python3 tools/loom_flow.py flow merge-ready --target . --item WI-576`
- `python3 tools/loom_status.py --target . --item WI-576`
- `make check`
