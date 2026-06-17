# WI-1511 Implementation Contract

## Change Class

- runtime
- contract
- test

## Ownership

The implementation owns only:

- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_flow.py`
- `.loom/bin/loom_flow.py`
- `skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- `examples/new-project/.loom/bin/loom_flow.py`
- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1511.md`
- `.loom/progress/WI-1511.md`
- `.loom/specs/WI-1511/**`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/runtime/gate-freeze/**` only as ignored runtime output during local validation

## Required Boundaries

- Gate freeze must record review/head binding details in `loom-gate-freeze/v1`.
- Fresh and allowed carrier-only review bindings may pass but must remain explicit evidence.
- Stale semantic drift, implementation drift, missing review, invalid review decision/kind, invalid semantic disposition, and validation-summary mismatch must block.
- Next action must distinguish carrier refresh from rerun review from PR head/body correction.
- Existing review, PR gate, controlled merge, release/no-release, and closeout semantics must not be weakened or replaced.

## Forbidden Changes

- No hosted workflow implementation.
- No GitHub host setting mutation.
- No release/tag/npm/GitHub Release changes.
- No raw/shadow/CI/GitHub review approval substitution.
- No ordinary implementation PR retained-review bypass.
