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
- Current Checkpoint: merge
- Current Stop: Scheduler review, carrier refresh, PR metadata readback, root governance, hosted loom-check/release checks, and local merge-ready inputs are stable for PR #1426 head 2c7bb79e407ae779fcf74326ff713258e7e63f8e; ready to consume PR gate and controlled merge.
- Next Step: Rerun local PR gate and hosted loom-pr-merge-gate on the refreshed head, then execute controlled merge and post-merge closeout if clean.
- Blockers: None
- Latest Validation Summary: Scheduler pre-review validation for WI-1394 passed after rebase and carrier activation: git diff --check; python3 tools/check_npm_package.py --help; python3 tools/check_npm_package.py --list-surfaces; python3 tools/py_compile_clean.py tools/check_npm_package.py; python3 tools/check_npm_package.py --surface npm-package-manifest; python3 tools/check_npm_package.py --surface npm-pack-payload; python3 tools/check_npm_package.py; make npm-package-manifest-check; make npm-pack-payload-check; make npm-package-check including npm run test:package; python3 tools/check_release_surface.py; python3 tools/loom.py suite inspect --target . --item WI-1394 --json; python3 tools/loom.py suite validate --target . --item WI-1394 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1394 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1394 --json; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_flow.py state-check --target . --item WI-1394; PR #1426 metadata preflight/readback passed and PR is ready-for-review. Implementation scope remains limited to tools/check_npm_package.py, Makefile package targets, and WI-1394 carriers/evidence.
- Recovery Boundary: Scope is issue #1394 only: `tools/check_npm_package.py` package validation surfaces, narrowly named Makefile package targets, WI-1394 minimal suite/progress carriers, PR metadata, local validation, and hosted-check readback. No #1393 release validator split, #1395 installed/global CLI smoke, #1396 docs/evidence convergence, parent #1260/#1255 closeout, release cutting, package payload content change, runtime behavior change, or scheduler-owned gate/review/merge/closeout.
- Current Lane: npm-package-validation-surfaces

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1393 after PR #1423 merged into `main` at 2026-06-10T22:11:32Z with merge commit `d459cc1488d2f6140925164fc4ab94fe54256e83`; issue #1393 closed at 2026-06-10T22:12:37Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1393 waiting-scheduler-gate report T1393-waiting-scheduler-gate-202606102155, ran current-head review/gate/controlled-merge readback, manually reconciled the native dependency edge #1260 blocked by #1393 after the tool apply path reported unsupported `add_blocked_by`, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1393 adds named release surface validator targets while preserving aggregate release surface validation; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, workflow publish behavior, package runtime behavior, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1393: hosted required checks passed on PR #1423 head `b5f1f466aa04c59f1fbb5aed45c1cc49c9bcc46a`; PR #1423 merged at `d459cc1488d2f6140925164fc4ab94fe54256e83`; issue #1393 closed; reconciliation audit passes after native dependency readback; local `fact-chain`, `state-check`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, suite validation, and `git diff --check` pass or are being revalidated on the closeout-only carrier branch.
- Lane Entry: release-surface-validator-split

## Sources

- Static Truth: .loom/work-items/WI-1394.md
- Dynamic Truth: .loom/progress/WI-1394.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
