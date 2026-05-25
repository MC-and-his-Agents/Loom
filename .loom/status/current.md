# Current Status

## Derived Fact Chain View

- Item ID: WI-1007
- Goal: Strengthen release/version/CLI checks so `loom` is the only active CLI line and `loom-installer` cannot be used as current CLI evidence for #1003.
- Scope: #1007: release surface checker, version/CLI release-check contract, installer package check wiring, and doc-sync needles needed to enforce installer legacy-only semantics.
- Execution Path: issue-scoped branch work/1007-checker-active-cli-evidence in /Users/mc/dev/Loom-1007-checker-active-cli-evidence
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1007.md
- Review Entry: .loom/reviews/WI-1007.json
- Validation Entry: python3 tools/check_release_surface.py
- Closing Condition: PR merged with checks rejecting `loom-installer` as active CLI/install/release evidence while preserving the legacy baseline as read-only evidence.
- Current Checkpoint: validated
- Current Stop: #1007 checker enforcement is implemented on the issue-scoped branch and local validation passes.
- Next Step: Record final reviews for the validated head, open PR, consume checks, then merge and close #1007.
- Blockers: None recorded.
- Latest Validation Summary: Passed: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; npm --prefix packages/loom-installer run check:release; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1007; make check.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1007-checker-active-cli-evidence on branch work/1007-checker-active-cli-evidence; keep scope limited to #1007 checker enforcement and related carrier updates.
- Current Lane: checker-active-cli-evidence

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:release; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1007.md
- Dynamic Truth: .loom/progress/WI-1007.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
