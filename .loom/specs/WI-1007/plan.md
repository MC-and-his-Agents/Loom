# WI-1007 Plan

1. Add negative release-surface scanning for statements that promote `loom-installer` or `loom-installer-v*` tags to active CLI/install/release evidence.
2. Extend `loom skills release-check --json` to expose the active CLI authority boundary.
3. Extend `tools/check_cli_contract.py` to assert the `skills release-check` authority boundary.
4. Wire installer package release checks to run `tools/check_release_surface.py`.
5. Strengthen doc-sync for the Codex default install path statement.
6. Validate release surface, version surface, CLI contract, installer checks, `make check`, and Loom carrier checks.
7. Open the issue-scoped PR for #1007 and consume PR/merge evidence before closing the issue.
