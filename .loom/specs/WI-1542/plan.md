# WI-1542 Plan

## Implementation Steps

1. Reuse existing purity and active workspace diagnostics as the startup audit input.
2. Add a runtime `work-item-audit` payload with schema `loom-active-carrier-audit/v1`.
3. Map host-complete carrier residue, stale carrier samples, shared workspace conflicts, and shadow freshness drift to existing classifier vocabulary and next actions.
4. Expose the runtime payload through `tools/loom.py workspace audit`.
5. Add focused regression coverage for blocking closeout residue, nonblocking stale terminal carriers, and shadow freshness drift.
6. Regenerate skills runtime copies and demo bootstrap fixtures.
7. Document the CLI matrix entry and verify PR metadata/readback before hosted checks.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/loom.py tools/check_cli_contract.py test/work_item_audit_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface work-item-audit`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `make loom-demo-new-project-check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py workspace audit --target . --json`
- `git diff --check`

## Dependencies

- Consumes existing active workspace diagnostics and stable classifier names from the #1513 lane.
- Provides startup audit evidence for #1515 final closeout readback.
- Does not block #1512/#1555 implementation beyond providing a reusable pre-start diagnostic surface.

## Scope Guard

- Do not implement hosted freeze admission, closeout-specific gate semantics, closeout queue UX, one-shot closeout run, or release/no-release decisions in this PR.
- Do not write GitHub issues, PR bodies, or shared milestone status from the runtime audit.
- Keep shared truth carrier writes limited to WI-1542 fact-chain/review/status/shadow refresh required for PR #1568.
