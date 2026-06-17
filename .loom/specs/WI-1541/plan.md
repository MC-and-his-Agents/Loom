# WI-1541 Plan

## Implementation Steps

1. Add `pr metadata-render`, `pr metadata-readback`, and `pr metadata-update` wrapper actions.
2. Add runtime `pr-metadata render/readback/update` payloads.
3. Render legacy Work Item/Branch/Head SHA bindings and the repo-specific `loom-repo-pr-metadata/v1` machine block.
4. Implement update as render -> `gh pr edit --body-file` -> host readback -> metadata preflight comparison.
5. Extend focused CLI contract coverage for wrapper delegation, render/readback behavior, closeout surface reuse, and generated runtime parity.
6. Update PR template guidance to use the Loom metadata-update flow.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py pr --help`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1541 --json`
- `git diff --check`

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: wrapper help and command matrix checks.
  - A2 -> test evidence: wrapper delegation checks in `tools/check_cli_contract.py`.
  - A3 -> test evidence: render/readback fixture checks against the governance metadata carrier.
  - A4 -> manual evidence: update wrapper contract now and live PR readback evidence after PR creation.
  - A5 -> test evidence: focused `pr-metadata` surface.
  - A6 -> structural check: generated-tree-drift check.

## Dependencies

- Consumes #1508 wrapper/runtime command surface hardening and #1554 wrapper argument contract.
- Provides PR metadata automation for #1514/#1534 docs/skills convergence and later #1512/#1533/#1515 PR body readback reduction.
- Does not block #1512 implementation semantics, but #1512/#1533/#1534 should consume this surface after it lands instead of hand-editing PR body machine blocks.

## Scope Guard

- Do not edit hosted workflow semantics.
- Do not edit closeout-specific gate behavior.
- Do not perform host issue mutation.
- Live PR body writes are allowed only through `metadata-update` on the #1541 PR after main-thread review/readback.
