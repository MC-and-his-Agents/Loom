# WI-1738 Plan

- Suite path consumed: minimal

## Implementation

| phase | work | validation |
| --- | --- | --- |
| P1 | Add ship binding inference from explicit inputs, PR readback, and checkout state. | `python3 -m py_compile tools/loom.py tools/check_cli_contract.py` |
| P2 | Pass effective branch/head/target bindings into ship delegated gates and closeout branch selection. | `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface ship-wrapper` |
| P3 | Add focused CLI contract regression for inferred PR bindings and conflict-safe output surface. | `git diff --check`; ship wrapper contract surface |

## Merge Boundary

This issue is limited to ship binding inference and the focused contract regression needed by PR #1738. Repair chain, review freshness, validation profile selection, and release closeout remain in their own issues.
