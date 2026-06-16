# WI-1507 Implementation Contract

## Change Class

- docs_governance
- contract

## Ownership

The implementation owns only:

- `docs/methodology/harness/gate-freeze.md`
- `docs/methodology/harness/README.md`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/work-items/WI-1507.md`
- `.loom/progress/WI-1507.md`
- `.loom/specs/WI-1507/**`
- `.loom/runtime/build/WI-1507.json`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/shadow/merge-ready-loom.json` and `.loom/shadow/closeout-loom.json` only as official shadow refreshes for `.loom/status/current.md`

## Required Boundaries

- The `loom-gate-freeze/v1` contract must not claim a CLI implementation exists.
- Planned command names must remain planned until #1508 adds them to `loom help --json`.
- Snapshot repair suggestions must be executable in the current command matrix or report `unsupported_command_surface`.
- The contract must not weaken authored review, PR gate, controlled merge, release/no-release, or closeout truth.
- Post-merge release evidence must not be represented as pre-merge present evidence.

## Forbidden Changes

- No changes to `.github/workflows`.
- No changes to PR templates.
- No changes to `tools/loom.py` command behavior.
- No generated skills payload sync.
- No release/tag/npm/GitHub Release changes.
