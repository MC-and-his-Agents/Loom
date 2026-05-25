# Current Status

## Derived Fact Chain View

- Item ID: WI-1006
- Goal: Migrate install and release documentation to the single active `loom` CLI line for #1003.
- Scope: #1006: root README files, adoption release/version/install docs, installer README files, doc-sync needles, and related distribution contract wording.
- Execution Path: issue-scoped branch work/1006-cli-docs-migration in /Users/mc/dev/Loom-1006-cli-docs-migration
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1006.md
- Review Entry: .loom/reviews/WI-1006.json
- Validation Entry: npm --prefix packages/loom-installer run check:docs
- Closing Condition: PR merged with docs no longer presenting `loom-installer` as the current CLI, recommended install path, active release line, or CLI release evidence.
- Current Checkpoint: local implementation before full validation.
- Current Stop: Documentation now labels `loom-installer` as a deprecated legacy artifact and keeps `loom` CLI as the only active release line; full validation is pending.
- Next Step: Run release/version/CLI/doc/installer checks, `make check`, Loom carrier checks, then open PR for #1006.
- Blockers: None recorded.
- Latest Validation Summary: Local checks passed for python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:docs; npm --prefix packages/loom-installer run check:versions; npm --prefix packages/loom-installer run check:payload; npm --prefix packages/loom-installer run check:distribution; python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1006. make check ran and exposed carrier-only gaps now being repaired.
- Recovery Boundary: Continue from /Users/mc/dev/Loom-1006-cli-docs-migration on branch work/1006-cli-docs-migration; keep scope limited to #1006 documentation migration and doc-sync/checker needle alignment.
- Current Lane: cli-docs-migration

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_cli_contract.py; npm --prefix packages/loom-installer run check:docs; make check
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1006.md
- Dynamic Truth: .loom/progress/WI-1006.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
