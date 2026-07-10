# WI-1742 Execution Breakdown

## Breakdown Units

| Unit | Scope | Files | Validation |
| --- | --- | --- | --- |
| EB-001 | Inline / host-only closeout e2e fixture | `tools/check_cli_contract.py` | py_compile; ship-wrapper fixture |
| EB-002 | Versioned terminal closeout admission fixture | `tools/check_cli_contract.py` | ship-wrapper fixture |
| EB-003 | Loom carriers and evidence | `.loom/work-items/WI-1742.md`, `.loom/progress/WI-1742.md`, `.loom/specs/WI-1742/**`, `.loom/status/current.md` | suite validate/evidence/carrier validate; carrier refresh; shadow parity |

## Dependencies

- Consumes closed #1737 checkpoint canonical enum.
- Consumes closed #1739 ship repair chain.
- Consumes closed #1741 validation profile selection.
- Blocks #1743 release closeout until merged and closed.

## Completion Boundary

WI-1742 is complete only after PR merge, issue closeout, carrier refresh, shadow parity, and terminal closeout sync.
