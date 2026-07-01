# WI-1869 Implementation Contract

## Scope

- Runtime implementation: `src/skills/shared/scripts/loom_flow.py` and generated runtime copies.
- CLI implementation: `tools/loom.py`.
- Contract tests: `tools/check_cli_contract.py` and release readback fixtures.
- Operator guidance: `README.md`, `README.zh-CN.md`, and `docs/methodology/harness/cli-command-matrix.md`.
- Carrier refresh: `.loom/bootstrap/init-result.json`, `.loom/bootstrap/manifest.json`, and `.loom/bin/loom_flow.py`.

## Required Behavior

- `reconciliation sync --apply` executes native `removeBlockedBy` actions planned from stale GitHub native dependency edges.
- `release readback` does not hide drift, but when drift is caused by checking from a closeout carrier head it returns the exact `--commit <release-merge-commit>` command.
- `review record --surface closeout` only works at a terminal closeout checkpoint and only writes carrier-only review metadata.
- Closeout hosted freeze/admission accepts carrier-only closeout review evidence only for terminal closeout surfaces.
- Help and docs prefer `loom closeout run ... --apply` as the common post-merge closeout path.

## Non-Goals

- No version bump.
- No npm/GitHub Release publish.
- No automatic merge.
- No new DSL.
- No semantic approval bypass.
