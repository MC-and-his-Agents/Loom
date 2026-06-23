# WI-1741 Execution Breakdown

## Breakdown Units

| Unit | Scope | Files | Validation |
| --- | --- | --- | --- |
| EB-001 | Ship validation profile selector and changed-path readback | `tools/loom.py` | py_compile; ship-wrapper fixture |
| EB-002 | Regression fixture coverage | `tools/check_cli_contract.py` | ship-wrapper fixture |
| EB-003 | Ship main-path docs | `README.md`, `README.zh-CN.md`, `docs/methodology/harness/cli-command-matrix.md` | ship docs contract; skills surface check |
| EB-004 | Loom carriers and evidence | `.loom/work-items/WI-1741.md`, `.loom/progress/WI-1741.md`, `.loom/specs/WI-1741/**`, `.loom/status/current.md` | suite validate/evidence/carrier validate |

## Dependencies

- Consumes #1735 ship contract and #1740 review freshness classification.
- Does not consume #1739 repair chain implementation.

## Completion Boundary

WI-1741 is complete only after PR merge, issue closeout, carrier refresh, shadow parity, and terminal closeout sync.
