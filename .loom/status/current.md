# Current Status

## Derived Fact Chain View

- Item ID: WI-1394
- Goal: Split tools/check_npm_package.py npm package validation into named, targetable manifest and payload surfaces while preserving aggregate npm package behavior.
- Scope: Issue #1394 only: tools/check_npm_package.py named npm-package-manifest and npm-pack-payload surfaces; aggregate npm package validation compatibility; Makefile package aliases; WI-1394 minimal suite/progress/review/current carrier; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1393 release validator work, #1395 installed/global CLI smoke, #1396 evidence convergence, parent #1260 closeout, umbrella #1255 closeout, release cutting, VERSION/tag/GitHub Release/npm publish, package payload content change, runtime behavior change, or external-visible release action.
- Execution Path: issue #1394 -> branch work/1394-npm-package-validation-surfaces -> PR #1426 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1394.md
- Review Entry: .loom/reviews/WI-1394.json
- Validation Entry: git diff --check; tools/check_npm_package.py --list-surfaces and targeted npm-package-manifest/npm-pack-payload surfaces; Makefile npm package aliases; aggregate check_npm_package.py; npm run test:package; check_release_surface.py compatibility; suite inspect/validate for WI-1394; fact-chain/state-check after scheduler activation; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1426 for #1394 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1394 is closed, and no_release closeout is consumable by #1260/#1255.
- Current Checkpoint: closed_out
- Current Stop: WI-1394 terminal closeout facts have been consumed: PR #1426 merged into `main` at 2026-06-10T23:23:45Z with merge commit `dcefb5df64f9fef1d747faeadf1dfda2d0921fc7`; issue #1394 closed at 2026-06-10T23:29:00Z; hosted required checks passed on head `d34c5beaf8bb87c40b2d9adf1a95419e52cb4230`; no_release terminal metadata is recorded in `.loom/progress/WI-1394.md`.
- Next Step: None for WI-1394. Installed/global CLI smoke and release/package convergence continue in #1395 and #1396; parent #1260 and umbrella #1255 consume this closeout later.
- Blockers: None
- Latest Validation Summary: Scheduler pre-review validation for WI-1394 passed after rebase and carrier activation: git diff --check; python3 tools/check_npm_package.py --help; python3 tools/check_npm_package.py --list-surfaces; python3 tools/py_compile_clean.py tools/check_npm_package.py; python3 tools/check_npm_package.py --surface npm-package-manifest; python3 tools/check_npm_package.py --surface npm-pack-payload; python3 tools/check_npm_package.py; make npm-package-manifest-check; make npm-pack-payload-check; make npm-package-check including npm run test:package; python3 tools/check_release_surface.py; python3 tools/loom.py suite inspect --target . --item WI-1394 --json; python3 tools/loom.py suite validate --target . --item WI-1394 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1394 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1394 --json; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_flow.py state-check --target . --item WI-1394; PR #1426 metadata preflight/readback passed and PR is ready-for-review. Implementation scope remains limited to tools/check_npm_package.py, Makefile package targets, and WI-1394 carriers/evidence.
- Recovery Boundary: WI-1394 is terminal. Do not reopen or modify implementation scope here; subsequent release/package stream work remains in #1395, #1396, parent #1260, and umbrella #1255.
- Current Lane: npm-package-validation-surfaces

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1394 after PR #1426 merged into `main` at 2026-06-10T23:23:45Z with merge commit `dcefb5df64f9fef1d747faeadf1dfda2d0921fc7`; issue #1394 closed at 2026-06-10T23:29:00Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1394 waiting-scheduler-gate report T1394-waiting-scheduler-gate-202606110610, ran current-head review/gate/controlled-merge readback, used Loom reconciliation sync to add closeout comment and close #1394, manually reconciled the native dependency edge #1260 blocked by #1394 after the tool apply path reported unsupported `add_blocked_by`, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1394 adds named npm package validation targets while preserving aggregate package validation; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, package payload content, runtime behavior, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1394: hosted required checks passed on PR #1426 head `d34c5beaf8bb87c40b2d9adf1a95419e52cb4230`; PR #1426 merged at `dcefb5df64f9fef1d747faeadf1dfda2d0921fc7`; issue #1394 closed; reconciliation audit and closeout check pass after native dependency readback; local `fact-chain`, `state-check`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, suite evidence/carrier validation, and `git diff --check` pass or are being revalidated on the closeout-only carrier branch.
- Lane Entry: npm-package-validation-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1394.md
- Dynamic Truth: .loom/progress/WI-1394.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
