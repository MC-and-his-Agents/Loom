# Current Status

## Derived Fact Chain View

- Item ID: WI-1393
- Goal: Split tools/check_release_surface.py release surface validation into named, targetable contract/workflow/guard surfaces while preserving aggregate release surface validation behavior.
- Scope: Issue #1393 only: tools/check_release_surface.py named release-doc-contract, release-workflow-contract, installer-sunset-guard, and forbidden-release-surface-patterns surfaces; Makefile aliases; docs/adoption/loom-cli-release-surface.md locator updates consuming the #1383 evidence contract; WI-1393 Loom carriers; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1394 npm package split, #1395 installed/global CLI smoke, #1396 docs/evidence convergence, release publishing, package/runtime behavior, hosted workflow semantic changes, parent #1260 closeout, umbrella #1255 closeout, or Round 9+ scope.
- Execution Path: issue #1393 -> branch work/1393-release-surface-validator-split -> PR #1423 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1393.md
- Review Entry: .loom/reviews/WI-1393.json
- Validation Entry: git diff --check; tools/check_release_surface.py --list-surfaces and targeted #1393 surfaces; Makefile release-surface aliases; aggregate check_release_surface.py; check_npm_package.py compatibility; suite inspect/validate for WI-1393; fact-chain/state-check after scheduler activation; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1423 for #1393 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1393 is closed, and no_release closeout is consumable by #1260/#1255.
- Current Checkpoint: merge
- Current Stop: Scheduler consumed T1393 waiting-scheduler-gate report for PR #1423 head `f71830b39ed7dc8c9cfd915fa6402b94960f9c58` and is binding WI-1393 root carrier/review state for merge-ready consumption after local validation, PR metadata/head readback, and hosted worker-relevant checks passed.
- Next Step: Complete scheduler-owned current-head review, PR gate, controlled merge, and no_release closeout/readback for PR #1423.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-10 local worker validation passed for the release surface split: `git diff --check`; `python3 tools/check_release_surface.py --help`; `python3 tools/check_release_surface.py --list-surfaces`; targeted `python3 tools/check_release_surface.py --surface release-doc-contract`, `--surface release-workflow-contract`, `--surface installer-sunset-guard`, and `--surface forbidden-release-surface-patterns`; aggregate `python3 tools/check_release_surface.py`; `python3 tools/check_release_surface.py --surface aggregate-release-surface --show-surface-evidence`; Makefile aliases for the four named release surfaces; `python3 tools/py_compile_clean.py tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; and `python3 tools/loom.py suite inspect --target . --item WI-1393 --json`. `python3 tools/loom.py suite validate --target . --item WI-1393 --json` returned `result=not_applicable`, `blocking_gaps=[]`, and `findings=[]` with the expected not_applicable exit classification for this suite path decision.
- Recovery Boundary: Only #1393 release surface validator split and minimal WI-1393 PR-readiness carriers are in scope. Do not implement #1394 npm package manifest/payload split, #1395 installed/global CLI smoke, #1396 docs/evidence convergence, parent #1260 closeout, umbrella #1255 closeout, release cutting, `VERSION`/tag/GitHub Release/npm publish changes, package runtime behavior, skills/demo/runtime regression changes, guardian/formal review, controlled merge, or `.loom/reviews/**` writes.
- Current Lane: release-surface-validator-split

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1405 after PR #1418 merged into `main` at 2026-06-10T21:01:08Z with merge commit `7c151d6e85c8d6b0609b4681ed1b80089e16811f`.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1405 waiting-scheduler-gate report T1405-report-202606110155-waiting-scheduler-gate, ran current-head review/gate/controlled-merge readback, and classified the controlled merge wrapper's local branch cleanup failure as post-host adapter cleanup after a successful merge.
- Diagnostics Entry: WI-1405 adds named runtime locking validation surfaces while preserving aggregate runtime regression validation; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, or external-visible runtime behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1405: hosted `loom-check` and rerun `loom-pr-merge-gate` passed on PR head `12c499eb1097878144f4ec7c49fa1f094e5a9009`; local `pr gate`, `flow merge-ready`, controlled merge check, `fact-chain`, `state-check`, `suite evidence validate`, `suite carrier validate`, `carrier refresh --dry-run`, and `git diff --check` passed.
- Lane Entry: runtime-locking-validation-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1393.md
- Dynamic Truth: .loom/progress/WI-1393.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
