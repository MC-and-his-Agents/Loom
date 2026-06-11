# Current Status

## Derived Fact Chain View

- Item ID: WI-1395
- Goal: Add installed/global CLI smoke as a named targetable release validation surface while preserving aggregate release/package validation behavior.
- Scope: Issue #1395 only: tools/check_release_surface.py installed-global-cli-smoke surface; Makefile release-surface-installed-global-cli-smoke alias; release evidence locator documentation; WI-1395 minimal suite/progress/review/current carrier; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1393 release surface semantic change, #1394 npm manifest/payload semantic change, #1396 release/package evidence convergence, parent #1260 closeout, umbrella #1255 closeout, VERSION/tag/GitHub Release/npm publish, workflow release behavior, package payload content change, external-visible release action, or user-global npm prefix mutation.
- Execution Path: issue #1395 -> branch work/1395-installed-global-cli-smoke -> PR #1434 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1395.md
- Review Entry: .loom/reviews/WI-1395.json
- Validation Entry: git diff --check; py_compile_clean; check_release_surface.py help/list-surfaces/installed-global-cli-smoke/aggregate; make release-surface-installed-global-cli-smoke-check; check_npm_package.py; npm run test:package; suite inspect/validate/evidence/carrier for WI-1395; fact-chain/state-check after scheduler activation; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1434 for #1395 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1395 is closed, and no_release closeout is consumable by #1260/#1255.
- Current Checkpoint: merge
- Current Stop: PR #1434 head `3d059d89600d60d465db4f10f35312cebce0d4d0` has scheduler-authored spec review, implementation review, current fact-chain/status/shadow carriers, PR metadata readback, and local PR gate evidence consuming the review as carrier-only drift after review/shadow carrier commits. Hosted implementation checks are running or passing on the same head.
- Next Step: Wait for hosted required checks on PR #1434 head `3d059d89600d60d465db4f10f35312cebce0d4d0`, rerun/consume `loom-pr-merge-gate` after current PR body metadata and carrier state are stable, then merge through the controlled path if all gates pass and consume no_release closeout for #1395 without closing parent #1260/#1255.
- Blockers: None
- Latest Validation Summary: Scheduler pre-review validation for WI-1395 passed after rebase and PR metadata refresh on head `f09fc9a1e8284f2245c123362563f19f24035c43`: `git diff --check`; `python3 tools/check_release_surface.py --help`; `python3 tools/check_release_surface.py --list-surfaces`; `python3 tools/py_compile_clean.py tools/check_release_surface.py`; `python3 tools/check_release_surface.py --surface installed-global-cli-smoke --show-surface-evidence`; `make release-surface-installed-global-cli-smoke-check`; `python3 tools/check_release_surface.py --surface aggregate-release-surface --show-surface-evidence` with `subsurface_count=5` and `installed-global-cli-smoke:pass`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `python3 tools/loom.py suite inspect --target . --item WI-1395 --json`; `python3 tools/loom.py suite validate --target . --item WI-1395 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1395 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1395 --json`; PR #1434 metadata preflight/readback passed for WI-1395, branch `work/1395-installed-global-cli-smoke`, head `f09fc9a1e8284f2245c123362563f19f24035c43`, and `closingIssuesReferences=[]`. Hosted `py-compile`, `demo-bootstrap`, `repo-local-cli`, and `release-judgment` passed on the current head; `loom-check`/`node-installer-pr-gate` were still in progress at scheduler readback, while root-governance/pr-merge-gate failures were classified as scheduler-owned carrier/review/metadata timing gaps rather than installed-global-cli-smoke semantic failures.
- Recovery Boundary: Scope is limited to `tools/check_release_surface.py`, `Makefile`, `docs/adoption/loom-cli-release-surface.md`, WI-1395 carriers/specs/review/current truth, and PR #1434 scheduler gate/closeout evidence. Do not cut a release, publish npm, change #1393/#1394 semantics, implement #1396 convergence, close parent #1260/#1255, alter VERSION/tag/GitHub Release state, change release workflow semantics, mutate the user's real global npm prefix, or start Round 9+ scope.
- Current Lane: installed-global-cli-smoke-release-surface

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1403 after PR #1425 merged into `main` at 2026-06-11T01:57:39Z with merge commit `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed at 2026-06-11T01:57:40Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1403 waiting-scheduler-gate report T1403-report-202606110557-waiting-scheduler-gate, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1262 blocked by #1403 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1403 adds a named demo bootstrap canonicalization diagnostic surface while preserving #1401 generation, fixture-drift, and aggregate demo bootstrap validation behavior; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, generated fixture content, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1403: hosted required checks passed on PR #1425 head `9be4d969f7781e05b9cd9fd06609a0a9d12292d5`; PR #1425 merged at `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed; reconciliation audit passes after native dependency readback; local `closeout check`, `closeout sync`, `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: demo-bootstrap-canonicalization-diagnostics

## Sources

- Static Truth: .loom/work-items/WI-1395.md
- Dynamic Truth: .loom/progress/WI-1395.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
