# WI-1488 Implementation Contract

- Suite path: minimal

## Allowed Changes

- README and README.zh-CN guidance for global `loom` CLI usage and context-safe output modes.
- Adoption and migration documentation that explains metadata-only host repository adoption, Codex user-level plugin usage, and legacy repo-local install residue.
- Harness CLI command matrix and source-repo regression notes that distinguish current downstream runtime support from historical/source-checkout diagnostics.
- `tools/loom.py help --json` output-mode descriptions.
- WI-1488 Loom carriers, suite artifacts, status, and shadow evidence needed to bind this documentation change to issue #1488 and PR #1669.

## Required Invariants

- Do not change runtime behavior, plugin payload implementation, installer behavior, release publishing, or downstream repository state in this Work Item.
- Do not reintroduce repo-local plugin/runtime/skills installation paths, single-skill package distribution, or old installer compatibility as supported downstream surfaces.
- Default user guidance must prefer global `loom` CLI, Codex user-level plugin, agent-safe summary/artifact-locator output, and explicit full diagnostics only for debugging, audit, or blocker classification.
- #1658 remains the release Work Item and must perform a new version bump after #1488 merges; v0.17.0 is not reused as this PR's release evidence.
- #1489 remains the final milestone regression and closeout consumer.

## Validation

- `python3 tools/loom.py help --json`
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 tools/loom.py suite validate --target . --item WI-1488 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1488 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1488 --json`
- `python3 tools/skills_surface.py check --surface docs-reference-sync`
- `npm --prefix packages/loom-installer run check:docs`
- `python3 tools/check_cli_contract.py`
- `python3 tools/loom_check.py --profile source --source-surface contract-only`
- `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- targeted legacy recommendation `rg`
- `git diff --check`
