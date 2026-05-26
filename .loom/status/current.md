# Current Status

## Derived Fact Chain View

- Item ID: WI-1068
- Goal: Strengthen checkers so the #1063 CLI-only install and release surface cannot regress after the #1067 documentation hard cut.
- Scope: #1068: checker-only guardrails for CLI-only install, root npm package payload, CLI-managed plugin/SKILLS payloads, and deprecated `loom-installer` evidence boundaries. No npm publish workflow, first npm release, installer publish reactivation, or broad CLI behavior rewrite.
- Execution Path: issue-scoped branch work/1068-cli-only-surface-checks in /Users/mc/dev/Loom-1068-cli-only-surface-checks
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1068.md
- Review Entry: .loom/reviews/WI-1068.json
- Validation Entry: python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; python3 tools/check_cli_contract.py; npm run test:package; npm run pack:dry-run; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1068; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1068; make check
- Closing Condition: #1068 is closed after its PR merges and #1069 can consume checkers that fail closed if primary docs, package payload, or release evidence drift away from the single root `loom` CLI install surface.
- Current Checkpoint: checker-hardening
- Current Stop: Local validation passed for CLI-only checker hardening, including release surface guards, root npm package payload guards, installer compatibility checks, Loom carrier checks, and full `make check`.
- Next Step: Commit and push the #1068 branch, open PR, run `pr-gate`, wait for PR checks, then merge and close #1068 with evidence for #1069.
- Blockers: None
- Latest Validation Summary: Passed `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `python3 tools/version_surface_check.py`; `python3 tools/check_cli_contract.py`; `npm run test:package`; `npm run pack:dry-run`; installer `check:docs`, `check:versions`, `check:payload`, and `check:distribution`; `fact-chain`; `shadow-parity`; `adopt verify`; and full `make check`.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1068-cli-only-surface-checks on branch work/1068-cli-only-surface-checks; keep scope limited to checker hardening and WI-1068 governance carriers.
- Current Lane: cli-only-surface-checks

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/check_npm_package.py; python3 tools/check_cli_contract.py; npm run test:package; npm run pack:dry-run; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1068; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1068; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1068.md
- Dynamic Truth: .loom/progress/WI-1068.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
