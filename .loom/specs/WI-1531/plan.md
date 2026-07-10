# WI-1531 Plan

## Implementation Steps

1. Add `loom-closeout-freeze/v1` terminal profile contract to the gate freeze methodology.
2. Link closeout gate consumption boundaries back to the terminal profile without changing closeout behavior.
3. Add a non-executable fixture inventory for closeout modes, pending fields, and failure kinds.
4. Refresh WI-1531 carriers and run focused local validation.

## Validation

- `git diff --check`
- `python3 -m json.tool docs/evidence/fixtures/closeout-freeze-terminal-profile-fixtures.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`

## Dependencies

- Parent FR: #1505.
- Hard dependencies: #1507 and #1508 closed; consumes already closed #1509 and #1511 as examples of terminal carrier and head binding pressure.
- Downstream dependencies: #1532 waits for #1531 and #1510; #1533 waits for #1532 and #1512; #1534 waits for #1533 and #1513; #1515 waits for #1514, #1529, and #1534.

## Scope Guard

- Do not implement #1510, #1512, #1513, #1532, #1533, #1534, or #1515 behavior in this PR.
- Do not modify runtime scripts, hosted workflows, PR templates, release workflows, package metadata, `VERSION`, tags, GitHub Releases, npm state, or external host settings.
