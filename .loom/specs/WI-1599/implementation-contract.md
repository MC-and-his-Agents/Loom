# WI-1599 Implementation Contract

- Suite path: minimal
- Work Item: WI-1599
- Issue: #1599
- PR: #1605

## Ownership

- Allowed writes: closeout check/run input contract, closeout PR role readback output, role fixtures, generated skill runtime mirrors, and demo bootstrap fixture updates caused by runtime sync.
- Forbidden writes: release publishing implementation, issue dependency parser semantics, host API auth behavior, PR metadata dry-run/update semantics, and milestone release closeout.

## Validation Contract

- Targeted checks must pass before review:
  - `python3 tools/loom.py workspace audit --target . --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
  - `python3 tools/skills_surface.py check`
  - `make loom-demo-new-project-check`
  - PR #1605 metadata readback/preflight against current head

## Review Boundary

Review consumes the focused diff and validation evidence above. Any expansion into release publishing, dependency parsing, host auth, or PR metadata behavior requires a separate Work Item.
