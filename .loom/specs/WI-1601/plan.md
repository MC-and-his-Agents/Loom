# WI-1601 Plan

## Implementation Steps

1. Add release readback inputs and output fields for release intent, tag, GitHub Release, npm, and workflow state.
2. Add release resume classification for complete, unpublished, partial, and conflicting states.
3. Add deterministic fixtures and CLI contract checks for release readback/resume.
4. Document the release readback CLI surface without replacing the GitHub Actions publish workflow.

## Validation

- `python3 tools/loom.py workspace audit --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
- `python3 tools/check_release_surface.py --surface release-doc-contract`
- `git diff --check`
- PR #1606 metadata readback/preflight against the current head

## Test Strategy

- Acceptance test mapping:
  - A1 -> test evidence: release readback fixture covering tag, GitHub Release, npm, and workflow state.
  - A2 -> test evidence: resume classification fixture covering complete, unpublished, partial, and conflicting release states.
  - A3 -> test evidence: CLI output fixture exposing next actions that keep GitHub Actions as publish authority.
  - A4 -> test evidence: release-readback fixture group and release surface contract check.

## Scope Guard

- Do not publish v0.15.0.
- Do not replace GitHub Actions release publishing.
- Do not change closeout PR role semantics.
- Do not change issue dependency parser semantics.
- Do not change host API auth behavior or PR metadata rendering.
