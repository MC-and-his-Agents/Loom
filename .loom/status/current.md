# Current Status

## Derived Fact Chain View

- Item ID: WI-1311
- Goal: Codify reusable merge-ready and closeout discipline in AGENTS.md.
- Scope: Add principle-level repository operating rules for docs-only contract freeze, suite not_applicable, review artifact timing, carrier/fact-chain/PR metadata alignment, post-merge closeout sync, shared gate blocker ownership, long-running check handling, and external host readback. Do not change runtime behavior, gates, templates, skills, release behavior, or documentation outside AGENTS.md.
- Execution Path: issue #1311 -> branch work/1311-agents-merge-closeout-discipline -> PR -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1311.md
- Review Entry: .loom/reviews/WI-1311.json
- Validation Entry: git diff --check; rg excluded incident-specific details; PR CI.
- Closing Condition: PR is merged to main, issue #1311 is closed with evidence, and the change remains limited to AGENTS.md governance rules.
- Current Checkpoint: closed
- Current Stop: PR #1312 merged to main at 2026-06-05T03:14:43Z with merge commit eae9f9753745cf0c1ec1a7a623904c4decd5315b; issue #1311 closed at 2026-06-05T03:14:45Z; local pr-gate and hosted loom-pr-merge-gate, loom-check, root-self-governance, repo-local-cli, py-compile, and demo-bootstrap passed before merge.
- Next Step: None; WI-1311 is terminal and retained only as AGENTS.md merge-ready/closeout discipline evidence.
- Blockers: None
- Latest Validation Summary: Post-merge closeout sync validation passed `git diff --check`, `python3 tools/loom.py fact-chain --target . --json`, and `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; pre-merge PR #1312 passed local pr-gate and hosted required checks on head b729f052ef2fe66a48644e4139af4db2355da67e before merge.
- Recovery Boundary: Terminal closeout carrier only. Do not resume WI-1311 implementation here; future AGENTS.md governance changes require separate issue-scoped work.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: PR #1312 local pr-gate, hosted required checks, and merge commit eae9f9753745cf0c1ec1a7a623904c4decd5315b
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1311.md
- Dynamic Truth: .loom/progress/WI-1311.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
