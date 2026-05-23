# WI-963 Implementation Contract

## Public Surface

- New methodology contract: `docs/methodology/harness/loom-check-runtime-purity.md`.
- New shared harness reference: `skills/shared/references/harness/loom-check-runtime-purity.md`.
- `loom_check` source self-check recognizes the contract as a required source surface and checks required anchors.

## Compatibility

- Existing `loom_check.py --profile auto|source|consumer` behavior remains unchanged.
- The change is documentation and contract validation only; it must not introduce runtime locks or change fixture generation behavior.
- Generated skill surfaces must remain synchronized through `tools/skills_surface.py`.

## Validation

- `git diff --check`
- `python3 tools/py_compile_clean.py tools/loom_check.py skills/shared/scripts/loom_check.py src/skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source .`
- PR #976 required checks and host-binding inspection
