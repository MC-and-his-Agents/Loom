# WI-1658 Implementation Contract

- Suite path: minimal

## Allowed Changes

- `VERSION` and root `package.json` bump from `v0.17.0` / `0.17.0` to `v0.17.1` / `0.17.1`.
- WI-1658 Work Item, progress, minimal suite, task carrier, evidence map, review, and release readiness evidence.
- Release PR metadata and closeout evidence needed to bind #1658 to the `v0.17.1` publish flow.

## Required Invariants

- Do not change runtime behavior, release workflow semantics, package payload layout semantics, or downstream repository state in the release-prep PR.
- Do not restore repo-local plugin/runtime/skills install paths, single-skill package distribution, or old installer compatibility as supported downstream surfaces.
- `v0.17.1` must be unoccupied before merge and must be published only by the authorized `loom-cli-release` main-push workflow or explicit repair workflow if the main-push publish is partially complete.
- The root npm package remains `@mc-and-his-agents/loom` with `loom` as the global CLI bin and Codex user-level plugin payload included under `plugins/loom`.
- Review approval is the authored Loom review record for the current PR/head; no non-author GitHub reviewer approval is required for this single-person repository.
- #1489 remains the final milestone regression and parent closeout consumer.

## Validation

- `python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `npm run test:package`
- `npm pack --dry-run --json --ignore-scripts`
- `python3 test/output_envelope_test.py`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py suite validate --target . --item WI-1658 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1658 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1658 --json`
- `python3 tools/loom.py fact-chain --target . --json`
- `git diff --check`
