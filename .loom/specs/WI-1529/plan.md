# WI-1529 Plan

## Implementation Steps

1. Add a `reference-integrity` skills surface to `tools/skills_surface.py`.
2. Extend local markdown/JSON reference scanning to distinguish install package, runtime copy, missing target, and outside-root diagnostics.
3. Add source/install/runtime parity checks for shared skill package assets.
4. Add focused fixtures for valid runtime references, missing runtime references, outside-root JSON references, and runtime copy drift.
5. Refresh WI-1529 carriers and run local validation before review and PR creation.

## Validation

- `python3 tools/py_compile_clean.py tools/skills_surface.py test/skills_surface_reference_integrity_test.py`
- `python3 test/skills_surface_reference_integrity_test.py`
- `python3 tools/skills_surface.py check --surface reference-integrity`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/skills_surface.py check`
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`

## Dependencies

- Parent FR: #1505.
- Soft dependency: #1514 final skill protocol wording can later link to this check surface if #1514 lands after #1529.
- Closeout dependency: #1515 must read back #1529 issue/PR/review/check evidence before milestone release/no-release closeout.

## Scope Guard

- Do not change review, merge-ready, gate freeze, PR gate, hosted admission, closeout profile, release/no-release, or skill content semantics.
- Do not update PR bodies, shared milestone carriers, `.loom/status/current.md` outside the WI-1529 active fact-chain entry, or other Work Item progress/review/shadow carriers.
- Do not add release artifacts, tags, version changes, npm/GitHub Release state, or external host settings.
