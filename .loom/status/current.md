# Current Status

## Derived Fact Chain View

- Item ID: WI-1402
- Goal: Split demo fixture drift and examples/new-project cleanliness validation into named targetable surfaces while preserving generation, canonicalization, fixture-drift, and aggregate demo bootstrap validation behavior.
- Scope: Issue #1402 only: tools/check_demo_bootstrap_fixture.py fixture-drift and examples/new-project cleanliness surfaces; Makefile fixture-drift/cleanliness aliases; WI-1402 suite/progress/review/current carrier; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1401 generation semantic change, #1403 canonicalization semantic change, #1404 docs/evidence convergence, parent #1262 closeout, fixture content change, generated runtime behavior change, release/package behavior, permissions, external-visible behavior, or Round 9+ scope.
- Execution Path: issue #1402 -> branch work/1402-demo-fixture-drift-cleanliness -> PR #1431 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1402.md
- Review Entry: .loom/reviews/WI-1402.json
- Validation Entry: git diff --check; tools/check_demo_bootstrap_fixture.py --surface generation/canonicalization/fixture-drift/cleanliness/aggregate; make loom-demo-new-project-check; make loom-demo-new-project-fixture-drift-check; make loom-demo-new-project-cleanliness-check; py_compile_clean; suite inspect/validate; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1431 for #1402 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1402 is closed, and no_release closeout is consumable by #1262/#1255.
- Current Checkpoint: merge
- Current Stop: PR #1431 head 81a722e896957346a42bf6063f9fdcc1cede9ecf has scheduler-authored semantic review, current PR metadata readback, and hosted implementation checks in progress or passing; scheduler is running pr-gate and controlled-merge checks.
- Next Step: Run PR gate and controlled-merge check on current head, wait for hosted required checks on the same head, then merge through the controlled path if all gates pass.
- Blockers: None
- Latest Validation Summary: Local validation passed for worker T1402 before PR creation: `git diff --check`; `python3 tools/check_demo_bootstrap_fixture.py --help`; Makefile dry-run surface readback for generation, canonicalization, fixture-drift, cleanliness, and aggregate targets; `python3 tools/check_demo_bootstrap_fixture.py --surface generation --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift --show-surface-evidence --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface cleanliness --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface aggregate --show-surface-evidence --timeout 180` with `subsurface_count=4`; `make loom-demo-new-project-check`; `make loom-demo-new-project-fixture-drift-check`; `make loom-demo-new-project-cleanliness-check`; `python3 tools/py_compile_clean.py tools/check_demo_bootstrap_fixture.py`; `python3 tools/loom.py suite inspect --target . --item WI-1402 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1402 --json` returned `result=not_applicable`, `blocking_gaps=[]`, exit 1 per current not_applicable contract; `git status --short --untracked-files=no -- examples/new-project` stayed empty after checks. PR #1431 metadata/body readback passed with the machine carrier aligned to branch `work/1402-demo-fixture-drift-cleanliness`; hosted `py-compile`, `demo-bootstrap`, and `repo-local-cli` passed on the implementation head, while `loom-pr-merge-gate`/`root-self-governance` were classified as scheduler-owned current-head review/gate gaps and long `loom-check` was still in progress at readback time.
- Recovery Boundary: Scope is limited to the demo bootstrap fixture drift and `examples/new-project` cleanliness validation surfaces. Do not redefine #1401 generation behavior, #1403 canonicalization diagnostics, #1404 docs/evidence convergence, parent #1262 closeout, fixture contents, release/package behavior, runtime behavior, permissions, or external-visible actions.
- Current Lane: demo-bootstrap-fixture-drift-cleanliness

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1403 after PR #1425 merged into `main` at 2026-06-11T01:57:39Z with merge commit `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed at 2026-06-11T01:57:40Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1403 waiting-scheduler-gate report T1403-report-202606110557-waiting-scheduler-gate, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1262 blocked by #1403 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1403 adds a named demo bootstrap canonicalization diagnostic surface while preserving #1401 generation, fixture-drift, and aggregate demo bootstrap validation behavior; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, generated fixture content, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1403: hosted required checks passed on PR #1425 head `9be4d969f7781e05b9cd9fd06609a0a9d12292d5`; PR #1425 merged at `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed; reconciliation audit passes after native dependency readback; local `closeout check`, `closeout sync`, `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: demo-bootstrap-canonicalization-diagnostics

## Sources

- Static Truth: .loom/work-items/WI-1402.md
- Dynamic Truth: .loom/progress/WI-1402.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
