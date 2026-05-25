# Implementation Contract

## Work Item

- Item ID: WI-1013
- GitHub FR: #1013
- Child Work Items: #1021, #1022, #1023
- PR: #1054

## Allowed Changes

- `VISION.md`
- `README.md`
- `docs/methodology/templates/spec-suite.md`
- `docs/evidence/extraction-ledger.md`
- `docs/evidence/landing-map.md`
- `.loom/work-items/WI-1013.md`
- `.loom/progress/WI-1013.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1013/**`
- `.loom/reviews/WI-1013*.json`
- `.loom/bootstrap/init-result.json` current item locator only

## Forbidden Changes

- No `docs/spec-kit/*`.
- No `.specify/`.
- No copied `/speckit.*` commands.
- No implementation of #1014, #1015, #1016, task carrier, gate-chain, or CLI automation contracts.

## Validation

- `git diff --check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- Targeted ledger/landing consistency check
- PR merge gate after review record refresh
