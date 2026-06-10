# Current Status

## Derived Fact Chain View

- Item ID: WI-1253
- Goal: Establish explicit fast and full validation entrypoints for daily CLI regressions so local iteration is narrower while merge-ready/release coverage remains complete.
- Scope: Issue #1253 / PR TBD only: daily-execution-cli fast/full source-surface entrypoints, Makefile aliases, mechanical self-check anchors, documentation alignment, WI-1253 carriers, validation evidence, and PR metadata; no #1254/#1247 work and no weakening of full merge-ready/release coverage.
- Execution Path: issue #1253 -> branch work/1253-fast-full-validation-entrypoints -> PR TBD -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1253.md
- Review Entry: .loom/reviews/WI-1253.json
- Validation Entry: git diff --check; make daily-execution-cli-fast; make daily-execution-cli-full; python3 tools/skills_surface.py check; python3 tools/check_cli_contract.py; suite inspect/validate for WI-1253; PR metadata preflight/readback; hosted checks
- Closing Condition: PR for #1253 is reviewed/gated by the scheduler on the current head, merged through controlled path, and no_release closeout is consumed without weakening full validation, repository truth boundaries, fail-closed behavior, or scheduler-owned gate semantics.
- Current Checkpoint: build
- Current Stop: PR #1414 is open on current head e44a7b73bd1b68745e0d6af6c20afe4df2966510 with worker-owned fast/full validation complete; scheduler is recording current-head review and refreshing carrier/shadow evidence.
- Next Step: Record scheduler current-head review for PR #1414, refresh carrier/shadow evidence, rerun PR gate/hosted checks, then controlled merge and no_release closeout if gates pass.
- Blockers: None worker-owned; remaining gate inputs are scheduler-owned current-head review and carrier/shadow refresh.
- Latest Validation Summary: Local validation passed for WI-1253: git diff --check; make py-compile; make daily-execution-cli-fast; make daily-execution-cli-full; python3 tools/skills_surface.py check; make loom-demo-new-project-check; python3 tools/check_cli_contract.py; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; suite inspect passed; suite validate returned result=not_applicable with blocking_gaps=[]; PR metadata preflight passed for PR #1414 head e44a7b73bd1b68745e0d6af6c20afe4df2966510. Scheduler purity-check and checkpoint build pass after terminalizing stale WI-1251 progress carrier.
- Recovery Boundary: WI-1253 only: daily-execution-cli fast/full validation entrypoints, Makefile aliases, mechanical self-check anchors, docs alignment, generated runtime copies, WI-1253 carriers, PR metadata, and validation evidence. No #1254/#1247 work, no full coverage weakening, no scheduler-owned review/PR gate/merge/release/closeout.
- Current Lane: daily-cli-fast-full-validation-entrypoints

## Runtime Evidence

- Run Entry: WI-1253 worker thread 019eb1da-9d0e-7790-aae8-18654bf035b6 activated branch work/1253-fast-full-validation-entrypoints and added fast/full daily-execution-cli validation entrypoints; PR is pending.
- Logs Entry: scheduler thread 019eaf94-f0bd-79a3-a396-83d6428b2777 dispatch T5-initial-202606102207-fast-full-validation-entrypoints; worker startup report T5-report-202606102207-instruction-ack-startup; local fast smoke command `make daily-execution-cli-fast`.
- Diagnostics Entry: WI-1253 separates local fast daily CLI smoke from full daily CLI bucket validation while preserving merge-ready/release authority, hosted checks, PR metadata, fact-chain, and scheduler-owned gates.
- Verification Entry: Local validation passed for WI-1253: git diff --check; make py-compile; make daily-execution-cli-fast; make daily-execution-cli-full; python3 tools/skills_surface.py check; make loom-demo-new-project-check; python3 tools/check_cli_contract.py; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_init.py verify --target .; suite inspect passed; suite validate returned result=not_applicable with blocking_gaps=[].
- Lane Entry: daily-cli-fast-full-validation-entrypoints

## Sources

- Static Truth: .loom/work-items/WI-1253.md
- Dynamic Truth: .loom/progress/WI-1253.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
