# Current Status

## Derived Fact Chain View

- Item ID: WI-1064
- Goal: Freeze the CLI-only install surface and root `loom` npm package contract for #1063.
- Scope: #1064: decision and contract only; no package implementation, npm publish workflow, README hard cut, or first release.
- Execution Path: issue-scoped branch work/1064-cli-only-install-contract in /Users/mc/dev/Loom-1064-cli-only-install-contract
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1064.md
- Review Entry: .loom/reviews/WI-1064.json
- Validation Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; make check
- Closing Condition: #1064 is closed after its PR merges and #1065-#1070 can cite docs/adoption/cli-only-install-contract.md as their frozen install/package contract.
- Current Checkpoint: validated
- Current Stop: CLI-only install contract has been authored and locally validated for #1064.
- Next Step: Commit, open PR, consume checks, merge, and close #1064.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1064; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1064; make check.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1064-cli-only-install-contract on branch work/1064-cli-only-install-contract; keep scope limited to contract/docs/governance carriers for #1064.
- Current Lane: cli-only-install-contract

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1064.md
- Dynamic Truth: .loom/progress/WI-1064.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
