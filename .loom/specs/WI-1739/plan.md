# WI-1739 Plan

## Phases

1. Insert repair chain
   - Add carrier refresh and shadow parity steps after safe metadata repair in `handle_ship`.
   - Stop before preflight and merge when either repair/readback step blocks.

2. Contract coverage
   - Update ship apply wrapper tests to assert the sequence:
     metadata update -> carrier refresh -> shadow parity -> metadata preflight -> PR gate -> controlled merge check.
   - Add a carrier refresh blocker fixture proving no preflight or merge happens after repair-chain failure.

3. Validation
   - Run `git diff --check`.
   - Run `tools/py_compile_clean.py` for changed Python files.
   - Run `tools/check_cli_contract.py --fixture-group ship-wrapper`.
   - Run `tools/check_cli_contract.py --surface pr-metadata`.
   - Run `tools/check_cli_contract.py --fixture-group closeout-wrapper`.

## Test Strategy

- Acceptance test mapping:
  - AC-1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`.
  - AC-2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`.
  - AC-3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`.
  - AC-4 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`.
  - AC-5 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`.
  - AC-6 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`.

## Rollback

Revert the ship repair-chain insertion and matching tests; this returns `loom ship --apply` to its prior explicit-command behavior.
