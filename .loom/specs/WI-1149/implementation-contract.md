# Implementation Contract

## Owned Change Surface

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/loom_check.py`
- generated skill runtime copies under `skills/*/.loom-runtime/shared/scripts/loom_check.py`
- `.loom/bin/loom_check.py`
- `examples/new-project/.loom/bin/loom_check.py`
- `.loom/work-items/WI-1149.md`
- `.loom/progress/WI-1149.md`
- `.loom/specs/WI-1149/*`

## Contract

- Missing full required artifact fixtures must block with `missing_required_artifact`.
- Minimal invalid skip-rationale fixtures must block with the expected invalid skip-rationale failure kind.
- Both fixtures must expose failure taxonomy, blocking gaps, remediation direction, and machine-readable missing input evidence.
- CLI output remains evidence only and must not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- #1149 must not implement evidence freshness, host conflict, scaffold, generated parity, PR gate, merge-ready, closeout, or parent reconciliation fixtures.
