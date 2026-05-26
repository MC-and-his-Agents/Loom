# Current Status

## Derived Fact Chain View

- Item ID: WI-1070
- Goal: Execute the first root `loom` CLI npm release and close out #1063 with release evidence.
- Scope: #1070 first npm publish for `@mc-and-his-agents/loom`, root VERSION/package version advance to an unpublished v* release, npm install smoke, GitHub tag/Release/workflow evidence, installer non-advancement evidence, and #1063 closeout evidence. No installer reactivation, new package name, Homebrew, standalone binary, or broader profile rewrite.
- Execution Path: issue #1070 -> branch work/1070-first-npm-cli-release -> worktree /Users/mc/dev/Loom-1070-first-npm-cli-release
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1070.md
- Review Entry: .loom/reviews/WI-1070.json
- Validation Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/check_cli_contract.py; npm run test:package; npm run pack:dry-run; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1070; python3 .loom/bin/loom_flow.py shadow-parity --target .; make check; merge commit checks; loom-cli-release workflow; npm install smoke
- Closing Condition: #1070 and #1063 close after PR merge, merge commit checks, `loom-cli-release` creates the new v* tag/GitHub Release and publishes matching `@mc-and-his-agents/loom` npm version, npm install smoke passes, and installer npm/tag state remains sunset/non-advancing.
- Current Checkpoint: first-npm-cli-release-prep
- Current Stop: Preparing a new unpublished root Loom CLI release version so the merged `loom-cli-release` workflow can create the v* tag, GitHub Release, and first `@mc-and-his-agents/loom` npm package publication.
- Next Step: Open PR, pass local and remote checks, merge, then consume `loom-cli-release` run, npm registry, tag, release, installer non-advancement, and #1063 closeout evidence.
- Blockers: None
- Latest Validation Summary: `python3 tools/check_release_surface.py`, `python3 tools/version_surface_check.py`, `python3 tools/check_npm_package.py`, `python3 tools/check_cli_contract.py`, `python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1070`, `npm run test:package`, `npm run pack:dry-run`, `python3 .loom/bin/loom_flow.py shadow-parity --target .`, installer `check:docs`, `check:versions`, `check:payload`, and `check:distribution` passed for v0.13.7 release prep; first `make check` reached only missing WI-1070 review carriers, which are being added before rerun.
- Recovery Boundary: Continue from `/Users/mc/dev/Loom-1070-first-npm-cli-release` on branch `work/1070-first-npm-cli-release`; do not publish manually outside the merged `loom-cli-release` workflow unless workflow evidence proves a permission-only blocker.
- Current Lane: first-npm-cli-release

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/check_cli_contract.py; npm run test:package; npm run pack:dry-run; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1070; python3 .loom/bin/loom_flow.py shadow-parity --target .; make check; merge commit checks; loom-cli-release workflow; npm install smoke
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1070.md
- Dynamic Truth: .loom/progress/WI-1070.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
