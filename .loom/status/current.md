# Current Status

## Derived Fact Chain View

- Item ID: WI-1008
- Goal: Allow the single active `loom` CLI release workflow to publish automatically after eligible `main` merges while preserving `workflow_dispatch` as a repair path.
- Scope: #1008: `loom-cli-release` main-push auto publish semantics, tag collision failure, release-surface documentation, checker needles, and Loom carriers for this work item.
- Execution Path: issue-scoped branch work/1008-cli-auto-release in /Users/mc/dev/Loom-1008-cli-auto-release
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1008.md
- Review Entry: .loom/reviews/WI-1008.json
- Validation Entry: python3 tools/check_release_surface.py
- Closing Condition: PR merged with `loom-cli-release` able to auto-create GitHub `v*` tag and Release on eligible `main` pushes, while tag collisions fail closed and installer publish evidence remains excluded.
- Current Checkpoint: validated
- Current Stop: #1008 workflow and release-surface changes are implemented locally; full local validation passes.
- Next Step: Commit validated implementation, open PR, consume checks, then merge and close #1008.
- Blockers: None recorded.
- Latest Validation Summary: Passed: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; ruby YAML parse for .github/workflows/loom-cli-release.yml; npm --prefix packages/loom-installer run check:release; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1008; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1008; make check. Python yaml module was unavailable locally, so Ruby stdlib YAML was used for syntax parsing.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1008-cli-auto-release on branch work/1008-cli-auto-release; keep scope limited to #1008 CLI auto-release workflow semantics, docs/checker needles, and carriers.
- Current Lane: cli-auto-release

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; ruby -e "require 'yaml'; YAML.load_file('.github/workflows/loom-cli-release.yml')"; npm --prefix packages/loom-installer run check:release; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1008.md
- Dynamic Truth: .loom/progress/WI-1008.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
