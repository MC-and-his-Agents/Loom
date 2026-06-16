# WI-1509 Plan

## Implementation Steps

1. Inspect existing `pr metadata-preflight` body-file evidence and `gate-freeze` payload assembly.
2. Add a dedicated PR body pin binding to `loom-gate-freeze/v1` that records rendered/readback body hashes, metadata block hashes, fingerprints, source locators, result, and next action.
3. Make gate freeze readiness block when the PR body pin binding reports rendered/readback drift or machine carrier identity mismatch.
4. Add focused CLI contract fixtures for pass and fail-closed PR body pin scenarios.
5. Sync shared runtime copies.
6. Refresh WI-1509 carriers and run focused local validation.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1509 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1509 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1509 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1509 --json`
- PR metadata preflight/readback and hosted checks before merge.

## Dependencies

- Parent FR: #1505.
- Hard dependencies: #1507 and #1508 merged and closed.
- Read-only references: issue #1509, existing `pr metadata-preflight` body-file evidence, and `loom-gate-freeze/v1` snapshot contract.

## Scope Guard

- Do not implement #1510-#1515 behavior in this PR.
- Do not modify `.github/workflows`, PR templates, release workflows, package metadata, `VERSION`, tags, GitHub Releases, npm state, or external host settings.
