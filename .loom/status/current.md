# Current Status

## Derived Fact Chain View

- Item ID: WI-1069
- Goal: Add automated npm publishing for the root `loom` CLI package while keeping GitHub `v*` tag, GitHub Release, and npm registry state consistent.
- Scope: #1069: `loom-cli-release` workflow publish automation, npm dry-run/precondition checks, `NPM_TOKEN` fail-closed behavior, release-surface documentation, and checker enforcement. No VERSION bump, first real npm publish, installer release reactivation, or #1070 closeout.
- Execution Path: issue-scoped branch work/1069-npm-cli-publish-workflow in /Users/mc/dev/Loom-1069-npm-cli-publish-workflow
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1069.md
- Review Entry: .loom/reviews/WI-1069.json
- Validation Entry: ruby YAML parse for `.github/workflows/loom-cli-release.yml`; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm run test:package; npm run pack:dry-run; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1069; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1069; make check
- Closing Condition: #1069 is closed after its PR merges and #1070 can consume a merge-checked workflow that validates npm package payloads, fails closed without `NPM_TOKEN` for real publishes, and reconciles `VERSION`, GitHub `v*` tag, GitHub Release, and `@mc-and-his-agents/loom` npm version state.
- Current Checkpoint: npm-publish-workflow
- Current Stop: Local validation passed on latest `origin/main` for `loom-cli-release` npm publish automation: Node setup, root npm package checks, dry-run pack, npm registry state resolution, `NPM_TOKEN` fail-closed publish, and GitHub tag/release/npm consistency decisions.
- Next Step: Bind review evidence, push PR, wait for PR checks, then merge and close #1069 with evidence for #1070.
- Blockers: None
- Latest Validation Summary: Passed `ruby` YAML parse for `.github/workflows/loom-cli-release.yml`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_cli_contract.py`; `npm run test:package`; `npm run pack:dry-run`; installer `check:docs`, `check:versions`, `check:payload`, and `check:distribution`; `fact-chain`; `shadow-parity`; `adopt verify`; and full `make check`. `npm view @mc-and-his-agents/loom` currently returns E404, so #1069 adds automation only and does not publish npm.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1069-npm-cli-publish-workflow on branch work/1069-npm-cli-publish-workflow; keep scope limited to npm publish workflow automation and WI-1069 governance carriers.
- Current Lane: npm-cli-publish-workflow

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: ruby YAML parse for `.github/workflows/loom-cli-release.yml`; python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm run test:package; npm run pack:dry-run; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1069; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1069; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1069.md
- Dynamic Truth: .loom/progress/WI-1069.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
