# WI-1529 Implementation Contract

## Work Item

- Work Item: WI-1529
- Issue: #1529
- Branch: `work/1529-skill-reference-integrity`

## Owned Write Surface

- `tools/skills_surface.py`
- `test/skills_surface_reference_integrity_test.py`
- `.loom/work-items/WI-1529.md`
- `.loom/progress/WI-1529.md`
- `.loom/reviews/WI-1529.json`
- `.loom/specs/WI-1529/`
- `.loom/bootstrap/init-result.json`
- `.loom/status/current.md`
- `.loom/shadow/closeout-loom.json`
- `.loom/shadow/merge-ready-loom.json`

## Required Behavior

- Add `reference-integrity` as an executable skills surface consumed by `python3 tools/skills_surface.py check`.
- Validate local markdown and JSON references from the correct package-relative base.
- Distinguish install-package references, runtime-copy references, missing targets, and outside-root references in diagnostics.
- Enforce source/install/runtime copy parity for shared SKILL package assets needed by generated packages and `.loom-runtime` copies.
- Keep anchor links and scheme links out of file-reference diagnostics.

## Forbidden Scope

- No review, merge-ready, gate freeze, PR gate, hosted admission, closeout profile, or release/no-release semantic changes.
- No migration of skill directories or external source layouts.
- No unrelated SKILL content rewrites except where the checker exposes a true broken reference.
- No #1510, #1512, #1513, #1531, #1532, #1533, #1534, or #1515 behavior changes.
- No release artifacts, tags, version changes, npm/GitHub Release state, or external host settings.

## Validation

- `python3 tools/py_compile_clean.py tools/skills_surface.py test/skills_surface_reference_integrity_test.py`
- `python3 test/skills_surface_reference_integrity_test.py`
- `python3 tools/skills_surface.py check --surface reference-integrity`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/skills_surface.py check --surface package-metadata`
- `python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1529 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `git diff --check`

## Consumer Boundary

The new surface may be consumed by skills checks, PR validation, hosted CI, milestone/12 release/no-release evidence, and #1515 closeout readback. It does not replace review, merge-ready, PR metadata, release judgment, hosted checks, or terminal closeout evidence.
