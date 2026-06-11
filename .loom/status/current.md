# Current Status

## Derived Fact Chain View

- Item ID: WI-1403
- Goal: Add demo bootstrap canonicalization diagnostics as a named targetable validation surface while preserving generation, fixture-drift, and aggregate demo bootstrap validation behavior.
- Scope: Issue #1403 only: tools/check_demo_bootstrap_fixture.py canonicalization diagnostics surface; Makefile alias; WI-1403 suite/progress/review/current carrier; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1401 generation semantic change, #1402 fixture drift/cleanliness split, #1404 docs/evidence convergence, parent #1262 closeout, fixture content change, generated runtime behavior change, release/package behavior, permissions, external-visible behavior, or Round 9+ scope.
- Execution Path: issue #1403 -> branch work/1403-demo-canonicalization-diagnostics -> PR #1425 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1403.md
- Review Entry: .loom/reviews/WI-1403.json
- Validation Entry: git diff --check; tools/check_demo_bootstrap_fixture.py --surface canonicalization/generation/fixture-drift/aggregate; make loom-demo-new-project-canonicalization-check; make loom-demo-new-project-check; py_compile_clean; suite inspect/validate; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1425 for #1403 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1403 is closed, and no_release closeout is consumable by #1262/#1255.
- Current Checkpoint: build
- Current Stop: Scheduler refreshed PR #1425 onto current `main` at head `dc9806f5f8eb1675ef9a88872a320967cced525a`; local validation and PR metadata/head/body readback passed for the refreshed head.
- Next Step: Record current-head scheduler review, rerun/consume PR gate and hosted checks, then run controlled merge and closeout sync if gates pass.
- Blockers: None
- Latest Validation Summary: Refreshed-head validation passed for PR #1425 head `dc9806f5f8eb1675ef9a88872a320967cced525a`: `git diff --check`; `python3 tools/check_demo_bootstrap_fixture.py --help`; `python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization --timeout 180`; `make loom-demo-new-project-canonicalization-check`; `python3 tools/check_demo_bootstrap_fixture.py --surface generation --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift --show-surface-evidence --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface aggregate --show-surface-evidence --timeout 180` with `subsurface_count=3`; `python3 tools/check_demo_bootstrap_fixture.py --surface aggregate --timeout 180`; `make loom-demo-new-project-check`; `python3 tools/py_compile_clean.py tools/check_demo_bootstrap_fixture.py`; `python3 tools/loom.py suite inspect --target . --item WI-1403 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1403 --json` returned `result=not_applicable`, `blocking_gaps=[]`, exit 1 per current not_applicable contract; PR metadata preflight/readback passed for `head_sha=dc9806f5f8eb1675ef9a88872a320967cced525a`; hosted worker-relevant checks started on current head and earlier stale PR-gate/root-governance failures were classified as scheduler-owned carrier/review metadata drift.
- Recovery Boundary: WI-1403 owns only demo bootstrap canonicalization diagnostics in `tools/check_demo_bootstrap_fixture.py`, a narrow Makefile target alias, WI-1403 suite/progress carriers, and PR metadata. It must not change #1401 generation semantics, #1402 fixture drift/cleanliness split, #1404 docs/evidence convergence, parent #1262 closeout, fixture contents, generated runtime behavior, release/package behavior, review artifacts, guardian/formal review, controlled merge, or closeout.
- Current Lane: demo-bootstrap-canonicalization-diagnostics

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1398 after PR #1424 merged into `main` at 2026-06-11T00:27:58Z with merge commit `8b6d40709e56f92a1b80360d8c77f6cc696d62e8`; issue #1398 closed at 2026-06-11T00:31:07Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1398 waiting-scheduler-gate report T1398-waiting-scheduler-gate-202606110556, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1261 blocked by #1398 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1398 adds named package-metadata and cache-artifacts skills validation surfaces while preserving #1397 docs-reference-sync/generated-tree-drift surfaces and aggregate skills validation; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, generated skills content, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1398: hosted required checks passed on PR #1424 head `d6f438caee77358486f16334dfe884387388482c`; PR #1424 merged at `8b6d40709e56f92a1b80360d8c77f6cc696d62e8`; issue #1398 closed; reconciliation audit passes after native dependency readback; local `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `closeout check`, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: skills-package-cache-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1403.md
- Dynamic Truth: .loom/progress/WI-1403.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
