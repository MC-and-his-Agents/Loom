# WI-1601 Implementation Contract

- Suite path: minimal
- Work Item: WI-1601
- Issue: #1601
- PR: #1606

## Ownership

- Allowed writes: release readback/resume CLI/runtime behavior, release-state fixtures, release readback docs, and targeted contract checks.
- Forbidden writes: GitHub Actions publishing replacement, v0.15.0 release closeout execution, closeout PR role model changes, issue dependency parser semantics, host API auth behavior, and PR metadata rendering/update semantics.

## Validation Contract

- Targeted checks must pass before review:
  - `python3 tools/loom.py workspace audit --target . --json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
  - `python3 tools/check_release_surface.py --surface release-doc-contract`
  - `git diff --check`
  - PR #1606 metadata readback/preflight against current head

## Review Boundary

Review consumes the focused release readback/resume diff and validation evidence above. Any expansion into release publishing, closeout role modeling, dependency parsing, host auth, or PR metadata behavior requires a separate Work Item.
