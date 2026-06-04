# Current Status

## Derived Fact Chain View

- Item ID: WI-1229
- Goal: Freeze the idle/no-active-item fact-chain schema and status surface contract for parent #1228.
- Scope: Define canonical active, terminal, and idle repository execution state; specify how `.loom/bootstrap/init-result.json` and `.loom/status/current.md` represent idle without fake active locators; document provenance, backward compatibility, retained items, and governance status boundaries. Terminal metadata writing, command split implementation, carrier closeout sync, repair/apply flows, and later #1230-#1237/#1296 work remain out of scope.
- Execution Path: issue #1229 -> branch work/1229-idle-fact-chain-contract -> PR #1298 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1229.md
- Review Entry: .loom/reviews/WI-1229.json
- Validation Entry: git diff --check; tools/check_loom_check_runtime_regressions.py; PR CI.
- Closing Condition: PR #1298 is merged to main, #1229 is closed with contract evidence, and follow-up idle implementation issues remain explicitly out of scope.
- Current Checkpoint: closed
- Current Stop: PR #1298 merged to main at 2026-06-04T21:08:32Z with merge commit b230263f908195f1ff12a59f7f123ed3afe187cc; issue #1229 closed at 2026-06-04T21:08:33Z; local pr-gate and hosted loom-pr-merge-gate, loom-check, root-self-governance, repo-local-cli, py-compile, and demo-bootstrap passed before merge.
- Next Step: None; WI-1229 is terminal and retained only as idle/no-active-item fact-chain and status surface contract evidence for the #1228 implementation sequence.
- Blockers: None
- Latest Validation Summary: Post-merge closeout sync validation passed `git diff --check`, `python3 tools/loom.py fact-chain --target . --json`, and `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; pre-merge PR #1298 passed local pr-gate and hosted required checks on head 563e5cb925af93e4c76125d700ccf0bafbf018d1 before merge.
- Recovery Boundary: Terminal closeout carrier only. Do not resume WI-1229 implementation here; terminal metadata writing, command split behavior, carrier closeout sync behavior, repair/apply behavior, runtime status/fact-chain implementation, release behavior, and #1230-#1237/#1296 follow-up work continue through separate #1228 child issues.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1298 local pr-gate, hosted required checks, and merge commit b230263f908195f1ff12a59f7f123ed3afe187cc
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1229.md
- Dynamic Truth: .loom/progress/WI-1229.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
