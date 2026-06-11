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
- Current Checkpoint: closed_out
- Current Stop: WI-1403 terminal closeout facts have been consumed: PR #1425 merged into `main` at 2026-06-11T01:57:39Z with merge commit `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed at 2026-06-11T01:57:40Z; hosted required checks passed on head `9be4d969f7781e05b9cd9fd06609a0a9d12292d5`; no_release terminal metadata is recorded in `.loom/progress/WI-1403.md`.
- Next Step: None for WI-1403. Fixture drift cleanliness and demo bootstrap docs/evidence convergence continue in #1402 and #1404; parent #1262 and umbrella #1255 consume this closeout later.
- Blockers: None
- Latest Validation Summary: Refreshed-head validation passed for PR #1425 head `dc9806f5f8eb1675ef9a88872a320967cced525a`: `git diff --check`; `python3 tools/check_demo_bootstrap_fixture.py --help`; `python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization --timeout 180`; `make loom-demo-new-project-canonicalization-check`; `python3 tools/check_demo_bootstrap_fixture.py --surface generation --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift --show-surface-evidence --timeout 180`; `python3 tools/check_demo_bootstrap_fixture.py --surface aggregate --show-surface-evidence --timeout 180` with `subsurface_count=3`; `python3 tools/check_demo_bootstrap_fixture.py --surface aggregate --timeout 180`; `make loom-demo-new-project-check`; `python3 tools/py_compile_clean.py tools/check_demo_bootstrap_fixture.py`; `python3 tools/loom.py suite inspect --target . --item WI-1403 --json` passed; `python3 tools/loom.py suite validate --target . --item WI-1403 --json` returned `result=not_applicable`, `blocking_gaps=[]`, exit 1 per current not_applicable contract; PR metadata preflight/readback passed for `head_sha=dc9806f5f8eb1675ef9a88872a320967cced525a`; hosted worker-relevant checks started on current head and earlier stale PR-gate/root-governance failures were classified as scheduler-owned carrier/review metadata drift.
- Recovery Boundary: WI-1403 is terminal. Do not reopen or modify implementation scope here; subsequent demo bootstrap stream work remains in #1402, #1404, parent #1262, and umbrella #1255.
- Current Lane: demo-bootstrap-canonicalization-diagnostics

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1403 after PR #1425 merged into `main` at 2026-06-11T01:57:39Z with merge commit `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed at 2026-06-11T01:57:40Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1403 waiting-scheduler-gate report T1403-report-202606110557-waiting-scheduler-gate, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1262 blocked by #1403 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1403 adds a named demo bootstrap canonicalization diagnostic surface while preserving #1401 generation, fixture-drift, and aggregate demo bootstrap validation behavior; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, generated fixture content, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1403: hosted required checks passed on PR #1425 head `9be4d969f7781e05b9cd9fd06609a0a9d12292d5`; PR #1425 merged at `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed; reconciliation audit passes after native dependency readback; local `closeout check`, `closeout sync`, `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: demo-bootstrap-canonicalization-diagnostics

## Sources

- Static Truth: .loom/work-items/WI-1403.md
- Dynamic Truth: .loom/progress/WI-1403.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
