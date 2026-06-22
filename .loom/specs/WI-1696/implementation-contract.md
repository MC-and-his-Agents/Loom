# WI-1696 Implementation Contract

## Ownership

- Main executor owns VERSION, package.json, WI-1696 carriers, release readiness evidence, PR metadata, release readback, and host closeout.

## Non-Goals

- Do not add new ship path implementation.
- Do not change release workflow semantics.
- Do not bump plugin surface version, host adapter version, skill contract versions, or deprecated installer versions.
- Do not close #1680 before #1696 release readback and issue closeout pass.

## Validation Contract

- Release PR head must pass local release/package validation and hosted checks.
- Published release closeout must read back tag, GitHub Release, npm version, release workflow run, issue #1696, phase #1680, and milestone #15 state.
