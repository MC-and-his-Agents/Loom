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
- Current Checkpoint: merge
- Current Stop: hosted checks green and local pr-gate passed; ready for controlled merge readback
- Next Step: merge PR #1305, then run closeout/readback before returning to A-D PR sequence
- Blockers: none
- Latest Validation Summary: 2026-06-04 final validation at d8f62124: local pr-gate passed; hosted checks all passed for PR #1305 including py-compile, demo-bootstrap, repo-local-cli, root-self-governance, loom-pr-merge-gate, release-judgment, node installer gate, and two loom-check jobs.
- Recovery Boundary: WI-1304 unblocker only; A-D PR branches remain read-only until #1305 is merged
- Current Lane: merge-ready

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
