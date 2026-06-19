# WI-1595 Implementation Contract

- Suite path: minimal
- Work Item: WI-1595
- Issue: #1595
- PR: #1603

## Ownership

- Allowed writes: PR metadata render/update/preflight runtime, wrapper forwarding, PR template/reference docs, generated skill runtime mirrors, targeted fixtures, and demo bootstrap fixture updates caused by runtime sync.
- Forbidden writes: host API auth, closeout PR role model, release resume/publishing logic, issue dependency parser semantics, and milestone release closeout.

## Validation Contract

- Targeted checks must pass before review:
  - `python3 tools/loom.py workspace audit --target . --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
  - `python3 tools/skills_surface.py check`
  - `make loom-demo-new-project-check`
  - PR #1603 metadata readback/preflight against current head

## Review Boundary

Review consumes the focused diff and validation evidence above. Any expansion into host auth, release resume, closeout role model, or dependency parsing requires a separate Work Item.
