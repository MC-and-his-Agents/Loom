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
- Current Checkpoint: release-judgment contract check fixed
- Current Stop: ready for current-head review refresh after check_cli_contract fix
- Next Step: record WI-1304 implementation review against current head f8e9f148, push PR #1305, update PR metadata, rerun pr-gate, then wait hosted CI
- Blockers: none
- Latest Validation Summary: 2026-06-04 local validation pass at f8e9f148: skills_surface check, git diff --check, check_demo_bootstrap_fixture.py, carrier refresh dry-run, loom_check contract-only, full make loom-check before release-judgment fixture fix, and python3 tools/check_cli_contract.py after the fixture fix.
- Recovery Boundary: WI-1304 unblocker only; A-D PR branches remain read-only until #1305 is green or merged
- Current Lane: merge-ready-prep

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
