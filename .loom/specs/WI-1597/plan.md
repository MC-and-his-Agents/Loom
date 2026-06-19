# WI-1597 Plan

## Implementation Steps

1. Route host REST reads through a shared `gh api` helper where local keyring auth is available.
2. Add CODEX-export bridge next-action guidance without globally exporting tokens.
3. Normalize unreadable/rate-limit/permission classifications across merge, check, closeout, and readback paths.
4. Regenerate skill runtime copies and synchronize demo bootstrap fixtures.

## Validation

- `python3 tools/loom.py workspace audit --target . --json`
- host adapter contract/check for authenticated REST and failure classifiers
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `python3 tools/skills_surface.py check`
- `make loom-demo-new-project-check`
- `git diff --check`
- PR #1607 metadata readback/preflight against the current head

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: host adapter fixtures and CLI contract checks for `gh api` preference.
  - A2 -> test evidence: anonymous rate-limit fixture classified as `host_api_unreadable`.
  - A3 -> test evidence: permission fixture classified as `permission`.
  - A4 -> test evidence: merge/check/closeout/readback contract surfaces using the shared helper path.

## Scope Guard

- Do not change PR metadata dry-run/update semantics.
- Do not change closeout PR role model.
- Do not change release resume or publishing behavior.
- Do not change issue dependency parser semantics.
