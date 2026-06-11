# Current Status

## Derived Fact Chain View

- Item ID: WI-1404
- Goal: Close the demo bootstrap validation split by documenting generation, canonicalization, fixture-drift, and examples/new-project cleanliness surfaces and recording parent closeout evidence.
- Scope: Issue #1404 only: concise demo bootstrap command/evidence references, WI-1404 progress and suite path decision carriers, PR metadata/head readback, and local validation evidence that consumes merged #1401/#1403/#1402 surfaces. No validation script behavior changes, fixture content or generation behavior changes, review/status/shadow writes, parent #1262/#1255 closeout, release/package/runtime implementation, guardian, formal review, controlled merge, or closeout.
- Execution Path: issue #1404 -> branch `work/1404-demo-docs-evidence` -> PR -> scheduler-owned review/pr-gate/controlled merge/no_release closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1404.md
- Review Entry: .loom/reviews/WI-1404.json
- Validation Entry: `git diff --check`; `python3 tools/check_demo_bootstrap_fixture.py --help`; `python3 tools/check_demo_bootstrap_fixture.py --surface generation --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift --show-surface-evidence --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface cleanliness --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface aggregate --show-surface-evidence --timeout 180`; `make loom-demo-new-project-check`; tracked `examples/new-project` cleanliness readback; WI-1404 suite inspect/validate; PR metadata/head readback; hosted checks classification.
- Closing Condition: PR for #1404 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1404 is closed, and no_release closeout lets #1262 consume explicit evidence for generation, canonicalization, fixture-drift, examples/new-project cleanliness, and aggregate fail-closed demo bootstrap validation.
- Current Checkpoint: merge
- Current Stop: Scheduler accepted watcher lane grant `watcher-lane-grant-R8-WI-1404-202606111557` for PR #1446 at exact head `2372cd5a5e723221cb03d25eb4cd83da2ce9b2c5`; WI-1404 fact-chain/status/review/shadow refresh and scheduler-owned gate are in progress.
- Next Step: Run scheduler-owned PR gate, merge-ready, and hosted/root-self-governance readback for PR #1446, then request merge_lane if controlled-merge ready.
- Blockers: None.
- Latest Validation Summary: Scheduler current-head readback for PR #1446 at head `2372cd5a5e723221cb03d25eb4cd83da2ce9b2c5`: PR #1446 OPEN/non-draft/MERGEABLE/BLOCKED with base `2d67609de1d21f9bf579506670f406125fcef7c0`; issue #1404 OPEN; parent #1262 OPEN; diff limited to WI-1404 docs/evidence/carrier/spec surfaces and harness docs; `git diff --check origin/main...HEAD` passed; `python3 tools/loom.py pr metadata-preflight 1446 --head-sha 2372cd5a5e723221cb03d25eb4cd83da2ce9b2c5 --work-item WI-1404 --surface merge_ready --json` passed; suite inspect passed; suite validate returned `result=not_applicable` with `blocking_gaps=[]`; suite evidence validate passed; suite carrier validate passed; hosted py-compile, demo-bootstrap, repo-local-cli, and loom-check passed; hosted loom-pr-merge-gate and root-self-governance failures were classified as expected before shared lane activation.
- Recovery Boundary: WI-1404/#1446 scheduler review/gate window only under watcher decision `watcher-lane-grant-R8-WI-1404-202606111557`. Do not process #1407, #1408, parent #1262 closeout, #1263, #1255, Round 9/11/Deferred, #1244/#1245/#1246, release/npm/live actions, VERSION/tag/GitHub Release/npm publish, workflow/runtime/package payload changes, or shared contract/schema/parser/failure vocabulary.
- Current Lane: scheduler-review-gate

## Runtime Evidence

- Run Entry: Scheduler accepted watcher shared/high-cost lane grant for WI-1404/#1446 and is refreshing fact-chain/status/review/shadow for current-head review and merge-ready evidence without parent #1262 closeout.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d owns WI-1404 gate/readback and any later merge_lane request.
- Diagnostics Entry: WI-1404 is docs/evidence convergence for demo bootstrap validation surfaces; it preserves aggregate demo bootstrap validation and does not change validation behavior, fixture content, generated runtime behavior, release/package behavior, workflows, shared parser/schema vocabulary, release execution, or live external state.
- Verification Entry: Scheduler validation passed at exact head 2372cd5a5e723221cb03d25eb4cd83da2ce9b2c5 after non-shared refresh onto origin/main 2d67609de1d21f9bf579506670f406125fcef7c0; PR metadata preflight, suite inspect, suite evidence validate, suite carrier validate, expected not_applicable suite validate, hosted loom-check, py-compile, demo-bootstrap, and repo-local-cli passed.
- Lane Entry: scheduler-review-gate

## Sources

- Static Truth: .loom/work-items/WI-1404.md
- Dynamic Truth: .loom/progress/WI-1404.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
