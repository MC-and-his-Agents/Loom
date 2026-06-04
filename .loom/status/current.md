# Current Status

## Derived Fact Chain View

- Item ID: WI-1239
- Goal: Freeze the global CLI runtime provider contract for downstream repositories under parent #1238.
- Scope: Define runtime provider taxonomy, provider authority boundaries, required `global-cli` command surface, metadata-only adoption relationship, compatibility mode, and migration boundary wording. Installed-state, doctor, verify, repair, migration, plugin registration, runtime execution behavior changes, and #1240-#1246 implementation work remain out of scope.
- Execution Path: issue #1239 -> branch work/1239-global-cli-provider-contract -> PR #1300 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1239.md
- Review Entry: .loom/reviews/WI-1239.json
- Validation Entry: git diff --check; tools/loom.py help --json; PR CI.
- Closing Condition: PR #1300 is merged to main, #1239 is closed with contract evidence, and follow-up global-cli provider implementation issues remain explicitly out of scope.
- Current Checkpoint: closed
- Current Stop: PR #1300 merged to main at 2026-06-04T20:14:25Z with merge commit 1676694c1f94f7bb384abbd6f9f890e3704d6729; issue #1239 closed at 2026-06-04T20:16:35Z; local pr-gate and hosted release-judgment, loom-pr-merge-gate, node-installer-pr-gate, and loom-check passed before merge.
- Next Step: None; WI-1239 is terminal and retained only as global CLI runtime provider contract evidence for the #1238 implementation sequence.
- Blockers: None
- Latest Validation Summary: Post-merge closeout sync validation passed `git diff --check`, `python3 tools/loom.py fact-chain --target . --json`, and `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; pre-merge PR #1300 passed local pr-gate and hosted required checks on head 96b0c851ecf73ffa775ce5c7c3f4b0fec0b0a35d before merge.
- Recovery Boundary: Terminal closeout carrier only. Do not resume WI-1239 implementation here; installed-state, doctor/verify, migration, repair, and downstream runtime work continue through separate #1238 follow-up issues.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1300 local pr-gate, hosted required checks, and merge commit 1676694c1f94f7bb384abbd6f9f890e3704d6729
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1239.md
- Dynamic Truth: .loom/progress/WI-1239.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
