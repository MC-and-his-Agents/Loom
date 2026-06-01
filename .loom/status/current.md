# Current Status

## Derived Fact Chain View

- Item ID: WI-877
- Goal: Implement repo-specific PR metadata parser preflight before review and merge-ready.
- Scope: #877 only: add parser preflight consumption for declared PR metadata machine carriers, structured diagnostics, and focused contract fixtures. Do not implement #874 PR body render/edit validation, #875 Markdown drift/legacy migration fixture expansion, #957 readiness/cost guard, or #1107 full spec suite CLI tree.
- Execution Path: issue #877 -> branch work/877-pr-metadata-parser-preflight -> workspace `.` in the checked out issue-scoped worktree recorded on issue #877 -> PR pending
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-877.md
- Review Entry: .loom/reviews/WI-877.json
- Validation Entry: git diff --check; focused rg for pre_review, pr-metadata-preflight, raw_excerpt_sha256, source_range_or_hash, metadata machine block; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_cli_contract.py after WI-877 carrier activation
- Closing Condition: PR merged to main, issue #877 closed completed, Project Loom Done, and closeout evidence records PR, head SHA, merge commit, target branch, validation, and Project truth.
- Current Checkpoint: build
- Current Stop: Parser preflight implementation and contract fixtures are integrated locally for #877.
- Next Step: Run full focused validation, author review record, open PR, wait required checks, controlled merge, and close out #877.
- Blockers: None recorded.
- Latest Validation Summary: Passing local evidence on 2026-06-01 so far: git diff --check; focused rg for pre_review, pr-metadata-preflight, raw_excerpt_sha256, source_range_or_hash, metadata machine block; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only . after repo companion pre_review validator sync.
- Recovery Boundary: #877 owns parser preflight consumption and diagnostics only; #874 render/edit validation, #875 Markdown drift/legacy migration fixture expansion, #957 readiness/cost guard, and #1107 full spec suite CLI tree remain out of scope.
- Current Lane: loom-hardening/pr-metadata-parser-preflight

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-877.md
- Dynamic Truth: .loom/progress/WI-877.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
