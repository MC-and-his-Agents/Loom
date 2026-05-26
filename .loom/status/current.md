# Current Status

## Derived Fact Chain View

- Item ID: WI-1067
- Goal: Hard-cut README and primary install/adoption docs to the CLI-only install entry for #1063.
- Scope: #1067: root `loom` CLI is the only primary install path; plugins and SKILLS are CLI-managed payloads; `loom-installer` may appear only as deprecated historical/evidence text. Minimal static doc-sync/checker needles may be updated only to stop requiring old documentation text. No #1068 checker hardening, npm publish workflow, first npm release, or installer release changes.
- Execution Path: issue-scoped branch work/1067-cli-only-doc-hard-cut in /Users/mc/dev/Loom-1067-cli-only-doc-hard-cut
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1067.md
- Review Entry: .loom/reviews/WI-1067.json
- Validation Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; python3 tools/check_npm_package.py; npm run test:package; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1067; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1067; make check
- Closing Condition: #1067 is closed after its PR merges and #1068 can consume primary docs that no longer present installer, plugin, or SKILLS as separate install surfaces.
- Current Checkpoint: document-hard-cut
- Current Stop: Primary README/adoption docs are hard-cut to root `loom` CLI install with CLI-managed plugin/SKILLS payloads; README compatibility text is explicitly non-primary and release-neutral.
- Next Step: Push refreshed #1067 head, wait for PR checks, then merge and close #1067 with PR/check evidence for #1068.
- Blockers: None
- Latest Validation Summary: Local validation passed after rebase onto main `c3d87cce44a842011f8b2c2898d97dd172d0eaab` at #1067 head `62e5fed3ad2df0e72e5bd1dd8fa6404c093b2e71`: `python3 tools/check_release_surface.py`; `python3 tools/version_surface_check.py`; `python3 tools/host_adapter_check.py`; `python3 tools/check_cli_contract.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `npm run pack:dry-run`; `npm --prefix packages/loom-installer run check:docs`; `npm --prefix packages/loom-installer run check:versions`; `npm --prefix packages/loom-installer run check:payload`; `npm --prefix packages/loom-installer run check:distribution`; `python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1067`; `python3 .loom/bin/loom_flow.py shadow-parity --target .`; `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1067`; `make check`.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1067-cli-only-doc-hard-cut on branch work/1067-cli-only-doc-hard-cut; keep scope limited to #1067 docs plus release-neutral stale doc/checker compatibility text.
- Current Lane: cli-only-doc-hard-cut

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; python3 tools/check_npm_package.py; npm run test:package; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1067; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1067; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1067.md
- Dynamic Truth: .loom/progress/WI-1067.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
