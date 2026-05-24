# WI-873 Implementation Contract

## Owned Surfaces

- `src/skills/shared/scripts/governance_surface.py`
- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `docs/adoption/repo-companion-contract.md`
- `docs/methodology/harness/pr-merge-gate.md`
- Generated shared references, root skills runtime surfaces, and demo runtime mirrors produced by `tools/skills_surface.py generate`
- `.loom` carriers for WI-873 review and closeout

## Required Behavior

- Loom core only defines the machine carrier envelope and parser/preflight contract.
- Repo-specific required field names remain declared by the repo companion.
- Malformed machine blocks fail closed with parser diagnostics instead of degrading into generic missing-field output.
- Absent blocks are non-blocking under `advisory_legacy` and blocking under `required`.
- Unsafe command locators or locator escapes fail closed.

## Verification Commands

- `python3 -m py_compile src/skills/shared/scripts/governance_surface.py src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py generate`
- `make check`
- `python3 tools/loom_check.py .`
- `git diff --check`
- Direct `python3 tools/loom_flow.py pr-metadata preflight ...` fixture checks for valid, malformed, and missing-field payloads
