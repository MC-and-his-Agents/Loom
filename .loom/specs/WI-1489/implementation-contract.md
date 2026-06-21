# WI-1489 Implementation Contract

- Suite path: minimal

## Allowed Changes

- WI-1489 Work Item, progress, minimal suite, task carrier, evidence map, review, and final closeout evidence.
- `.loom/status/current.md` and shadow carriers needed to make WI-1489 the active closeout item.
- GitHub issue/PR metadata and closeout comments for #1489, #1480, and #1476 after merge.

## Required Invariants

- Do not change runtime behavior, package payload, release workflow semantics, or published release artifacts.
- Do not restore repo-local plugin/runtime/skills install paths, single-skill package distribution, or old installer compatibility as supported paths.
- Do not perform downstream repository migration.
- #1493 is consumed as closeout identity-binding hardening only.
- Single-person development does not require a non-author GitHub reviewer; required approval truth is an authored Loom review record consumed by PR gate.

## Validation

- `python3 test/output_envelope_test.py`
- `python3 tools/loom.py help --json`
- `python3 tools/skills_surface.py check`
- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py release readback --target . --version v0.17.1 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit 3e17dd73fb4ccb260ede68e5518b83aa904fb682 --release-judgment release_required --json`
- `python3 tools/loom.py suite validate --target . --item WI-1489 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1489 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1489 --json`
- `python3 tools/loom.py fact-chain --target . --json`
- `git diff --check`
