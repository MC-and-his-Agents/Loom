# Current Status

## Derived Fact Chain View

- Item ID: WI-1304
- Goal: Teach governance maturity to consume docs-only suite_path not_applicable when an approved spec_review record exists.
- Scope: Update governance_surface maturity detection so formal_spec_or_not_applicable can satisfy the standard spec gate without requiring plan.md for docs-only contract freeze work. Keep review, PR head binding, CI, fact-chain, closeout, and suite rationale requirements intact.
- Execution Path: issue #1304 -> branch work/1304-docs-only-governance-maturity -> PR -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1304.md
- Review Entry: .loom/reviews/WI-1304.json
- Validation Entry: git diff --check; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py governance-profile status --target /Users/mc/dev/Loom-worktrees/1264-regression-surface-contract --host github; python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .
- Closing Condition: PR for #1304 is merged and PR-A can consume docs-only not_applicable maturity after rebasing onto main.
- Current Checkpoint: build
- Current Stop: Governance maturity recognizes docs-only suite_path not_applicable only when an approved spec_review record exists; runtime copies, bootstrap hashes, suite carriers, and shadow surfaces are synchronized.
- Next Step: Push branch, open #1304 PR, run pr-gate against the PR head, and wait for hosted checks before merge.
- Blockers: None
- Latest Validation Summary: Passed on 2026-06-04: git diff --check; python3 tools/loom.py suite validate --target . --item WI-1304 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1304 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1304 --json; python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py fact-chain --target .; python3 .loom/bin/loom_flow.py shadow-parity --target .; python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run; python3 .loom/bin/loom_flow.py governance-profile status --target /Users/mc/dev/Loom-worktrees/1264-regression-surface-contract --host github returned strong; python3 tools/loom_check.py --profile source --source-surface bootstrap-regression . passed; make loom-demo-new-project-check passed after fixture sync.
- Recovery Boundary: Keep #1304 limited to governance maturity consumption of docs-only not_applicable suite path decisions and runtime copy/hash sync. Do not change suite validation, PR head binding, implementation review, CI, fact-chain, closeout, or A-D contract PR content.
- Current Lane: gate-unblocker/docs-only-governance-maturity

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; suite validate; tools/check_cli_contract.py; PR/CI
- Lane Entry: implementation

## Sources

- Static Truth: .loom/work-items/WI-1304.md
- Dynamic Truth: .loom/progress/WI-1304.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
