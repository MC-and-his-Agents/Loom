# Current Status

## Derived Fact Chain View

- Item ID: WI-876
- Goal: Define the repo-specific PR metadata machine carrier contract.
- Scope: #876 only: freeze PR metadata machine carrier schema fields, PR body human/machine boundary, legacy migration mode, and generated skills reference sync. Do not implement #877 parser behavior, #874 render/edit validation, #875 fixtures, or #957 readiness guard.
- Execution Path: issue #876 -> branch work/876-pr-metadata-machine-carrier -> workspace `.` in the checked out issue-scoped worktree recorded on issue #876 -> PR #1191
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-876.md
- Review Entry: .loom/reviews/WI-876.json
- Validation Entry: git diff --check; focused rg carrier contract/readability check; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/loom.py suite validate --target . --item WI-876 --json; python3 tools/loom.py suite evidence validate --target . --item WI-876 --json; python3 tools/loom.py suite carrier validate --target . --item WI-876 --json
- Closing Condition: PR #1191 merged to main, issue #876 closed completed, Project Loom Done, and closeout evidence records PR, head SHA, merge commit, target branch, validation, and Project truth.
- Current Checkpoint: merge
- Current Stop: PR metadata machine carrier contract is implemented, reviewed, and ready for PR gate on PR #1191.
- Next Step: Refresh PR body with WI-876 binding, rerun PR gate, then merge and close out #876.
- Blockers: None recorded.
- Latest Validation Summary: Passing local evidence on 2026-05-31: git diff --check; focused rg for carrier_id, repo_specific_field_set, source_range_or_hash, required_fields, rendered_hash, free Markdown, and machine carrier; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/loom.py suite validate --target . --item WI-876 --json; python3 tools/loom.py suite evidence validate --target . --item WI-876 --json; python3 tools/loom.py suite carrier validate --target . --item WI-876 --json.
- Recovery Boundary: #876 owns PR metadata machine carrier contract docs, PR template human/machine boundary text, generated skills reference sync, and WI-876 carriers only; #877 parser behavior, #874 render/edit validation, #875 fixtures, and #957 readiness guard remain out of scope.
- Current Lane: loom-hardening/pr-metadata-machine-carrier

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-876.md
- Dynamic Truth: .loom/progress/WI-876.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
