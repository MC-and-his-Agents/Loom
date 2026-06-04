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
- Current Stop: Local implementation, fixture sync, fact-chain, suite, review, metadata, release-judgment contract check, and pr-gate inputs are ready for PR #1305 merge-gate consumption.
- Next Step: Refresh WI-1304 current-head review after the release-judgment fix, push PR #1305, wait for hosted checks, then run merge-ready/controlled merge readback before returning to PR-A.
- Blockers: None
- Latest Validation Summary: Passed on 2026-06-04 at head a463c31d33c6188193ede3e7dae9a2fca6b6f57b: git diff --check; python3 -m py_compile tools/check_cli_contract.py; python3 tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1304 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1304 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1304 --json; python3 .loom/bin/loom_flow.py fact-chain --target .; python3 .loom/bin/loom_flow.py shadow-parity --target .; Pending after review refresh: carrier refresh dry-run, pr-gate, hosted CI.
- Recovery Boundary: Keep #1304 limited to governance maturity consumption of docs-only not_applicable suite path decisions, runtime copy/hash sync, and release-judgment contract-check fixture isolation. Do not change suite validation, PR head binding, implementation review, CI, fact-chain, closeout, or A-D contract PR content.
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
