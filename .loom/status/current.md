# Current Status

## Derived Fact Chain View

- Item ID: WI-1597
- Goal: Harden host API authentication and unreadable/permission classification.
- Scope: Issue #1597 only: prefer gh keyring-backed REST calls, provide CODEX_EXPORT_GH_TOKEN bridge guidance, classify anonymous REST rate limit as host_api_unreadable, classify permission failures separately, and cover merge/check/closeout/readback host API call paths with targeted fixtures; do not change PR metadata dry-run semantics, closeout PR role model, release resume, or issue dependency parser behavior.
- Execution Path: issue #1597 -> branch work/1597-host-api-auth -> PR #1607 -> merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1597.md
- Review Entry: .loom/reviews/WI-1597.json
- Validation Entry: workspace audit; py_compile_clean; host adapter contract check; check_cli_contract; skills_surface check; demo bootstrap fixture check; PR metadata readback/preflight; hosted loom-check
- Closing Condition: Issue #1597 and PR #1607 are terminal only after host auth behavior, fact-chain, spec review, implementation review, hosted checks, target branch, release/no-release evidence, and closeout evidence are consistent.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-1597 is ready for PR #1607 merge gate: host API auth implementation, minimal suite, evidence map, and task carrier are in place.
- Next Step: Record current-head spec and implementation reviews, refresh shadow carriers, update PR #1607 metadata, and wait for hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-19 WI-1597 merge-ready validation: workspace audit passed; py_compile_clean passed; host adapter/auth classifier checks passed; check_cli_contract passed; skills_surface check passed; make loom-demo-new-project-check passed; suite validate passed; suite evidence validate passed; suite carrier validate passed; PR #1607 metadata readback/preflight must be re-read after final carrier-only head update; hosted demo-bootstrap, repo-local-cli, root-self-governance, and py-compile had passed after fixture sync; hosted loom-check/node-installer/release-judgment pending at last readback.
- Recovery Boundary: Work item carrier, minimal suite, evidence map, task carrier, review records, PR metadata, and shadow carrier for #1597 / PR #1607 only.
- Current Lane: Host API auth lane

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1515 v0.14.2 release-required closeout preparation
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: #1515 is release_required because #1554/#1555 shipped CLI/runtime behavior after v0.14.1; v0.14.2 release PR merge remains publish-capable and requires explicit user approval before merge.
- Verification Entry: pre-merge release validation passed for the WI-1515 v0.14.2 release payload and PR #1591 metadata: version/release/npm/package/skills/CLI contract/suite/fact-chain/audit/build/review/shadow checks passed; PR metadata render/readback/preflight passed; post-merge release evidence remains pending.
- Lane Entry: milestone-12-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1597.md
- Dynamic Truth: .loom/progress/WI-1597.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
