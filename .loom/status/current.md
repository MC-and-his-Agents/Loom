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
- Current Checkpoint: build
- Current Stop: AGENTS.md now carries the reusable merge-ready and closeout discipline rules for docs-only contract freeze, suite not_applicable, review artifact timing, carrier/PR metadata alignment, post-merge closeout sync, shared gate blocker ownership, long-running checks, and host readback.
- Next Step: Run local validation, record review evidence, update PR metadata, and consume hosted checks before merge.
- Blockers: None
- Latest Validation Summary: `git diff --check` passed; `python3 tools/loom.py fact-chain --target . --json` passed for WI-1311; `python3 tools/loom.py suite validate --target . --item WI-1311 --json` returned `result=not_applicable` with no blocking gaps; excluded incident-specific detail scan passed for AGENTS.md.
- Recovery Boundary: Keep this PR limited to AGENTS.md governance discipline and WI-1311 Loom carriers. Do not change runtime behavior, gates, templates, skills, release behavior, or documentation outside AGENTS.md.
- Current Lane: governance-docs/merge-closeout-discipline

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; excluded incident-specific detail scan; PR CI
- Lane Entry: governance-docs/merge-closeout-discipline

## Sources

- Static Truth: .loom/work-items/WI-1311.md
- Dynamic Truth: .loom/progress/WI-1311.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
