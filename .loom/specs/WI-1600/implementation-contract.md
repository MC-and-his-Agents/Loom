# WI-1600 Implementation Contract

- Suite path: minimal
- Work Item: WI-1600
- Issue: #1600
- PR: #1604

## Ownership

- Allowed writes: dependency graph/parser semantics, provenance vocabulary, parser fixtures, generated skill runtime mirrors, docs/skill references to dependency source semantics, and demo bootstrap fixture updates caused by runtime sync.
- Forbidden writes: closeout PR role model, release resume/publishing logic, host API auth behavior, PR metadata dry-run/update semantics, and milestone release closeout.

## Validation Contract

- Targeted checks must pass before review:
  - `python3 tools/loom.py workspace audit --target . --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
  - `python3 tools/skills_surface.py check`
  - `make loom-demo-new-project-check`
  - PR #1604 metadata readback/preflight against current head

## Review Boundary

Review consumes the focused diff and validation evidence above. Any expansion into closeout roles, release resume, host auth, or PR metadata behavior requires a separate Work Item.
