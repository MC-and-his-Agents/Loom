# WI-874 Plan

- Suite path: minimal

1. Read #876/#877 machine carrier and parser contracts plus current PR template guidance.
2. Extend PR metadata preflight to accept rendered body files and optional post-edit/readback body files.
3. Compare declared machine block hashes between rendered and read-back bodies without treating human Markdown drift as failure.
4. Update CLI wrapper and focused fixtures for body-file and compare-body-file paths.
5. Update PR template / methodology docs with safe `gh pr edit --body-file` guidance and truth boundary.
6. Sync generated skills surface and validate with whitespace, focused rg, skills surface, source contract-only loom_check, CLI contract, suite checks, PR gate, controlled merge, reconciliation, and closeout checks as appropriate.

## Validation Mapping

- Acceptance 1 -> `python3 tools/loom.py pr metadata-preflight --body-file .github/PULL_REQUEST_TEMPLATE.md --json`.
- Acceptance 2 -> `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Acceptance 3 -> focused `rg` for `compare_body_file`, `body_artifact`, and `machine block drift`.
- Acceptance 4 -> focused `rg` for `gh pr edit --body-file` and `--compare-body-file`.
- Acceptance 5 -> focused `rg` for body artifact truth-boundary docs and unchanged Work Item/review/merge-ready/closeout authority.
