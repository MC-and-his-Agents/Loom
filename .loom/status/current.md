# Current Status

## Derived Fact Chain View

- Item ID: WI-1065
- Goal: Implement the root `loom` npm package payload and bin entry for #1063.
- Scope: #1065: package manifest, npm bin shim, package payload checks, and local pack/install smoke only; no npm publish workflow, README hard cut, or installer release changes.
- Execution Path: issue-scoped branch work/1065-root-loom-npm-package in /Users/mc/dev/Loom-1065-root-loom-npm-package
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1065.md
- Review Entry: .loom/reviews/WI-1065.json
- Validation Entry: python3 tools/check_npm_package.py; npm run test:package; npm pack --dry-run --json --ignore-scripts; local npm install smoke; python3 tools/check_cli_contract.py; make check
- Closing Condition: #1065 is closed after its PR merges and #1066 can consume a root npm package whose `loom` bin runs the current CLI from the packaged payload.
- Current Checkpoint: validated
- Current Stop: Root npm package payload and `loom` bin entry have been implemented and locally validated for #1065.
- Next Step: Commit, open PR, consume checks, merge, and close #1065.
- Blockers: None
- Latest Validation Summary: Passed: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; python3 tools/check_npm_package.py; npm run test:package; npm pack --pack-destination with local npm install smoke for loom --help, loom version --json, and loom detect --target <empty-dir> --json; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1065; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1065; make check.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1065-root-loom-npm-package on branch work/1065-root-loom-npm-package; keep scope limited to root npm package payload/bin and #1065 governance carriers.
- Current Lane: root-loom-npm-package

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_npm_package.py; npm run test:package; npm pack --dry-run --json --ignore-scripts; local npm install smoke; python3 tools/check_cli_contract.py; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1065.md
- Dynamic Truth: .loom/progress/WI-1065.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
