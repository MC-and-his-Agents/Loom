# Current Status

## Derived Fact Chain View

- Item ID: WI-875
- Goal: Cover PR metadata Markdown drift, broken machine carrier diagnostics, and legacy migration fixtures.
- Scope: #875 only: focused parser fixture hardening for Markdown drift, negative carrier envelopes, unsupported parser version, readback hash drift, and advisory/dual_read legacy migration. Do not implement #957 readiness/cost guard or #1107 full spec suite CLI tree.
- Execution Path: issue #875 -> branch work/875-pr-metadata-drift-legacy-fixtures -> workspace `/Users/mc/dev/Loom-worktrees/875-pr-metadata-drift-legacy-fixtures` -> PR #1194.
- Workspace Entry: /Users/mc/dev/Loom-worktrees/875-pr-metadata-drift-legacy-fixtures
- Recovery Entry: .loom/progress/WI-875.md
- Review Entry: .loom/reviews/WI-875.json
- Validation Entry: git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_cli_contract.py
- Closing Condition: PR #1194 merged to main, issue #875 closed completed, Project Loom Done, and closeout evidence records PR, head SHA, merge commit, target branch, validation, and Project truth.
- Current Checkpoint: build
- Current Stop: PR #1194 is open for #875 with local fact-chain, suite, shadow parity, loom_check, and CLI contract validation passing on the updated evidence commit.
- Next Step: Push PR binding evidence, wait for required checks, then run PR gate, controlled merge, reconciliation, and closeout.
- Blockers: None recorded.
- Latest Validation Summary: Passing local evidence on 2026-06-01 for PR #1194 head after evidence refresh: `git diff --check`; focused `rg` for `PR_METADATA_SUPPORTED_PARSER_VERSIONS`, `unsupported parser_version`, `missing-schema`, `dual-read-legacy`, `raw_excerpt_sha256`, `gh_pr_edit_body_file_readback`, and shell command substitution fixture text; `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`; `python3 tools/check_cli_contract.py`; `python3 tools/loom.py suite validate --target . --item WI-875 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-875 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-875 --json`; `python3 tools/loom.py fact-chain --target . --json`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --blocking`; direct unsupported parser-version smoke returned blocking diagnostics with block locator and expected parser version.
- Recovery Boundary: #875 owns parser/fixture hardening only; #957 readiness/cost guard, #1107 full spec suite CLI tree, and any replacement of Work Item/review/merge-ready/closeout truth remain out of scope.
- Current Lane: loom-hardening/pr-metadata-drift-legacy-fixtures

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: loom-hardening/pr-metadata-drift-legacy-fixtures

## Sources

- Static Truth: .loom/work-items/WI-875.md
- Dynamic Truth: .loom/progress/WI-875.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
