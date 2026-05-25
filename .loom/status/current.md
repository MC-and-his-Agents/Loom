# Current Status

## Derived Fact Chain View

- Item ID: WI-1009
- Goal: Execute and verify the first `loom` CLI automatic release after #1008 enabled main-push publishing.
- Scope: #1009: choose root `VERSION`, update generated version surfaces, merge an issue-scoped PR that triggers `loom-cli-release`, and record CLI tag/release plus no-installer-publish evidence.
- Execution Path: issue-scoped branch work/1009-first-cli-release in /Users/mc/dev/Loom-1009-first-cli-release
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1009.md
- Review Entry: .loom/reviews/WI-1009.json
- Validation Entry: python3 tools/version_surface_check.py
- Closing Condition: PR merged with new `v0.13.0` tag and GitHub Release pointing at the #1009 merge commit, while installer npm latest and `loom-installer-v*` releases remain unchanged.
- Current Checkpoint: validated
- Current Stop: #1009 release candidate is committed at 964e1a21ed9712916229918243fa4acae3b35365 with root VERSION v0.13.0 and local validation passing.
- Next Step: Open PR, consume checks, merge, then verify the v0.13.0 tag/release and installer non-advancement evidence.
- Blockers: None recorded.
- Latest Validation Summary: Passed: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1009; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1009; make check. A transient host-binding REST read failure was isolated by rerunning the exact host-binding command successfully before the final make check pass.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1009-first-cli-release on branch work/1009-first-cli-release; keep scope limited to #1009 first CLI release VERSION bump, generated version surfaces, release readiness evidence, and carriers.
- Current Lane: first-cli-release

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:release; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1009.md
- Dynamic Truth: .loom/progress/WI-1009.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
