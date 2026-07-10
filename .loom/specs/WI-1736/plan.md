# WI-1736 Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1736/spec.md
- Scenario locators: .loom/specs/WI-1736/spec.md#s1-apply-output-reflects-post-apply-state, .loom/specs/WI-1736/spec.md#s2-dry-run-remains-non-mutating
- Acceptance locators: .loom/specs/WI-1736/spec.md#acceptance-criteria
- Plan locator: .loom/specs/WI-1736/plan.md
- Provenance: GitHub issue #1736.
- Freshness rule: Re-run validation after carrier refresh runtime, generated mirror, fixture, or plugin payload metadata changes.

## Implementation

1. Recompute carrier refresh state after apply/write mutation.
2. Preserve dry-run reporting as non-mutating pre-apply diagnostics.
3. Update source, generated skills, plugin runtime, and demo bootstrap runtime copies together.
4. Add or preserve focused regression coverage for apply readback.
5. Refresh plugin payload hash and WI-1736 Loom carriers.

## Validation

- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper`
- A1 -> `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`
- A2 -> `PYTHONDONTWRITEBYTECODE=1 python3 test/work_item_audit_test.py`
- A3 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper`
- Plugin payload -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`
- Syntax / whitespace -> `git diff --check`

## Constraints

- Keep the change limited to #1736 readback behavior and generated mirror/hash sync.
- Do not implement ship pre-repair orchestration, review stale policy, validation profile selection, closeout policy, or release behavior.
