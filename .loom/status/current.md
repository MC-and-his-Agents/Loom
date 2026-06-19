# Current Status

## Derived Fact Chain View

- Item ID: WI-1600
- Goal: Disable issue prose active dependency inference.
- Scope: Issue #1600 only: stop treating issue prose as active dependencies, consume only GitHub native dependency relationships or structured Loom machine blocks, and update parser fixtures/docs for dependency provenance; do not change docs convergence or closeout PR role behavior.
- Execution Path: issue #1600 -> branch work/1600-native-dependency-only -> PR #1604 -> merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1600.md
- Review Entry: .loom/reviews/WI-1600.json
- Validation Entry: workspace audit; py_compile_clean; check_cli_contract --surface governance-closeout/dependency parser; skills_surface check; demo bootstrap fixture check; PR metadata readback/preflight; hosted loom-check
- Closing Condition: Issue #1600 and PR #1604 are terminal only after dependency parser behavior, fact-chain, spec review, implementation review, hosted checks, target branch, release/no-release evidence, and closeout evidence are consistent.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-1600 is ready for PR #1604 merge gate: dependency parser implementation, minimal suite, evidence map, and task carrier are in place.
- Next Step: Record current-head spec and implementation reviews, refresh shadow carriers, update PR #1604 metadata, and wait for hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-19 WI-1600 merge-ready validation: workspace audit passed; py_compile_clean passed; check_cli_contract --surface governance-closeout passed; skills_surface check passed; make loom-demo-new-project-check passed; suite validate passed; suite evidence validate passed; suite carrier validate passed; PR #1604 metadata readback/preflight must be re-read after final carrier-only head update; hosted demo-bootstrap, repo-local-cli, root-self-governance, and py-compile had passed after fixture sync; hosted loom-check/node-installer/release-judgment pending at last readback.
- Recovery Boundary: Work item carrier, minimal suite, evidence map, task carrier, review records, PR metadata, and shadow carrier for #1600 / PR #1604 only.
- Current Lane: Issue dependency parser lane

## Runtime Evidence

- Run Entry: 2026-06-19 WI-1515 v0.14.2 release-required closeout preparation
- Logs Entry: local command output retained in current Codex milestone/12 thread
- Diagnostics Entry: #1515 is release_required because #1554/#1555 shipped CLI/runtime behavior after v0.14.1; v0.14.2 release PR merge remains publish-capable and requires explicit user approval before merge.
- Verification Entry: pre-merge release validation passed for the WI-1515 v0.14.2 release payload and PR #1591 metadata: version/release/npm/package/skills/CLI contract/suite/fact-chain/audit/build/review/shadow checks passed; PR metadata render/readback/preflight passed; post-merge release evidence remains pending.
- Lane Entry: milestone-12-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1600.md
- Dynamic Truth: .loom/progress/WI-1600.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
