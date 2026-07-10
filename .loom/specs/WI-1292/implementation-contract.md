# Implementation Contract

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1292/spec.md
- Plan locator: .loom/specs/WI-1292/plan.md
- Evidence map locator: .loom/specs/WI-1292/evidence-map.md
- Task carrier locator: .loom/specs/WI-1292/task-carrier.md

## Change Boundary

- Allowed implementation files:
  - `tools/check_cli_contract.py`
  - `docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json`
- Allowed governance carrier files:
  - `.loom/work-items/WI-1292.md`
  - `.loom/progress/WI-1292.md`
  - `.loom/status/current.md`
  - `.loom/specs/WI-1292/*`
  - `.loom/shadow/merge-ready-loom.json`
  - `.loom/shadow/closeout-loom.json`
  - `.loom/progress/WI-1452.md` terminal closeout checkpoint sync
- Forbidden implementation files:
  - `src/skills/shared/scripts/loom_flow.py`
  - `skills/shared/scripts/loom_flow.py`
  - generated runtime copies under `skills/*/.loom-runtime/`
  - release/version/npm surfaces owned by WI-1293

## Behavioral Commitments

- Required-check enforcement remains unchanged.
- #1292 only consumes #1452 triggered-check rollup behavior through regression fixtures and inventory.
- WebEnvoy/Syvert failed and pending non-required triggered checks block controlled merge while required checks remain green.
- HotCP-style CI-only, post-merge review, and stale/head drift signals fail closed at review/PR gate surfaces.

## Verification Contract

- `python3 -m py_compile tools/check_cli_contract.py`
- `python3 -m json.tool docs/evidence/fixtures/complex-existing-authority-migration-fixtures.json >/dev/null`
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`
- `python3 tools/loom.py suite validate --target . --item WI-1292 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1292 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1292 --json`
- `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
