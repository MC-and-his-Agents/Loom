# WI-1597 Implementation Contract

- Suite path: minimal
- Work Item: WI-1597
- Issue: #1597
- PR: #1607

## Ownership

- Allowed writes: host adapter/auth/readback/classifier runtime, shared generated skill runtime mirrors, targeted host API fixtures, and demo bootstrap fixture updates caused by runtime sync.
- Forbidden writes: PR metadata dry-run/update semantics, closeout PR role model, release resume/publishing logic, issue dependency parser semantics, and milestone release closeout.

## Validation Contract

- Targeted checks must pass before review:
  - `python3 tools/loom.py workspace audit --target . --json`
  - host adapter contract/check for authenticated REST and failure classifiers
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
  - `python3 tools/skills_surface.py check`
  - `make loom-demo-new-project-check`
  - PR #1607 metadata readback/preflight against current head

## Review Boundary

Review consumes the focused diff and validation evidence above. Any expansion into PR metadata behavior, closeout role model, release resume, or dependency parsing requires a separate Work Item.
