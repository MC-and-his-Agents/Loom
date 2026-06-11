# Current Status

## Derived Fact Chain View

- Item ID: WI-1399
- Goal: Add targetable per-skill launcher smoke validation while preserving the aggregate skills surface command.
- Scope: Issue #1399 only: tools/skills_surface.py launcher-smoke surface and --skill filter; aggregate skills validation compatibility; #1397 docs-reference-sync/generated-tree-drift and #1398 package-metadata/cache-artifacts surfaces preserved; Makefile skills-launcher-smoke-check alias; WI-1399 not_applicable suite/progress/review/current carrier; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1400 docs/evidence convergence, parent #1261 closeout, umbrella #1255 closeout, release/package/demo/runtime behavior changes, generated skills content change, hosted workflow semantic change, permissions change, external-visible behavior, or Round 9+ scope.
- Execution Path: issue #1399 -> branch work/1399-skills-launcher-smoke-surface -> PR #1432 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1399.md
- Review Entry: .loom/reviews/WI-1399.json
- Validation Entry: git diff --check; skills_surface.py help/list-surfaces and targeted launcher-smoke/docs-reference-sync/generated-tree-drift/package-metadata/cache-artifacts surfaces; make skills-launcher-smoke-check; aggregate tools/skills_surface.py check; tools/loom.py skills check; py_compile_clean; suite inspect/validate for WI-1399; fact-chain/state-check after scheduler activation; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1432 for #1399 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1399 is closed, and no_release closeout is consumable by #1261/#1255.
- Current Checkpoint: build
- Current Stop: Scheduler rebased PR #1432 onto current main, resolved the Makefile target conflict, refreshed PR body metadata/readback for head a5f9c2da4b0aec75a12a2a657620d30811cc0d4c, activated WI-1399 carrier state, and completed local pre-review validation including source contract checks.
- Next Step: Commit and push scheduler carrier activation for WI-1399, refresh PR metadata for the new head, run pre-review, record current-head semantic review, run PR gate and controlled merge if checks pass, then perform no_release closeout for WI-1399.
- Blockers: None
- Latest Validation Summary: Scheduler validation on rebased head a5f9c2da4b0aec75a12a2a657620d30811cc0d4c passed: git diff --check; python3 tools/skills_surface.py check --list-surfaces; python3 tools/skills_surface.py check --surface launcher-smoke --skill loom-init; python3 tools/skills_surface.py check --surface launcher-smoke; make skills-launcher-smoke-check SKILL=loom-init; python3 tools/skills_surface.py check --surface docs-reference-sync; python3 tools/skills_surface.py check --surface generated-tree-drift; python3 tools/skills_surface.py check --surface package-metadata; python3 tools/skills_surface.py check --surface cache-artifacts; python3 tools/skills_surface.py check; python3 tools/loom.py skills check --target . --json; python3 tools/py_compile_clean.py tools/skills_surface.py; python3 tools/loom.py suite inspect --target . --item WI-1399 --json; python3 tools/loom.py suite validate --target . --item WI-1399 --json returned result=not_applicable with blocking_gaps=[] and exit 1 per not_applicable contract; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_cli_contract.py. PR #1432 metadata preflight/readback passed for branch work/1399-skills-launcher-smoke-surface and head a5f9c2da4b0aec75a12a2a657620d30811cc0d4c with machine block comparison status=match. Earlier hosted root-self-governance and loom-pr-merge-gate failures were classified as stale scheduler-owned carrier/review state from the old head, not launcher-smoke semantic failures.
- Recovery Boundary: WI-1399 scope is limited to per-skill launcher smoke validation, aggregate skills check preservation, existing #1397/#1398 surface preservation, PR metadata/head readback, scheduler-owned review/pr-gate/controlled merge/no_release closeout. #1400 docs/evidence convergence, parent #1261 closeout, umbrella #1255 closeout, release/package/demo/runtime behavior, generated skills content changes, permissions, external-visible behavior, and Round 9+ scope are out of scope.
- Current Lane: skills-launcher-smoke-surface

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1403 after PR #1425 merged into `main` at 2026-06-11T01:57:39Z with merge commit `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed at 2026-06-11T01:57:40Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1403 waiting-scheduler-gate report T1403-report-202606110557-waiting-scheduler-gate, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1262 blocked by #1403 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1403 adds a named demo bootstrap canonicalization diagnostic surface while preserving #1401 generation, fixture-drift, and aggregate demo bootstrap validation behavior; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, generated fixture content, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1403: hosted required checks passed on PR #1425 head `9be4d969f7781e05b9cd9fd06609a0a9d12292d5`; PR #1425 merged at `bc7ceb0cc0f89a7c3662633edcc17cb6a40b65a7`; issue #1403 closed; reconciliation audit passes after native dependency readback; local `closeout check`, `closeout sync`, `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: demo-bootstrap-canonicalization-diagnostics

## Sources

- Static Truth: .loom/work-items/WI-1399.md
- Dynamic Truth: .loom/progress/WI-1399.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
