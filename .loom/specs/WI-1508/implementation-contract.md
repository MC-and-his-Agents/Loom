# WI-1508 Implementation Contract

## Change Class

- runtime
- contract
- docs_governance

## Ownership

The implementation owns only:

- `tools/loom.py`
- `src/skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_flow.py`
- `.loom/bin/loom_flow.py`
- `skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- `examples/new-project/.loom/bin/loom_flow.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/work-items/WI-1508.md`
- `.loom/progress/WI-1508.md`
- `.loom/specs/WI-1508/**`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/runtime/gate-freeze/**` only as ignored runtime output during local validation

## Required Boundaries

- `loom gate freeze check` must be read-only.
- `loom gate freeze write` must write only a repo-local runtime artifact.
- Missing or stale gate input must fail closed with machine-readable diagnostics.
- Existing PR metadata, shadow parity, suite validation, review/head, release/no-release, PR gate, controlled merge, and closeout semantics must not be weakened or replaced.
- Repair suggestions must reference commands present in the current command matrix or report an unsupported command surface.

## Forbidden Changes

- No changes to `.github/workflows`.
- No changes to PR templates.
- No GitHub host writes from the freeze command.
- No PR body hash pin semantics.
- No hosted admission workflow implementation.
- No release/tag/npm/GitHub Release changes.
