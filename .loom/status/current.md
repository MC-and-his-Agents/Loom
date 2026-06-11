# Current Status

## Derived Fact Chain View

- Item ID: WI-1398
- Goal: Split tools/skills_surface.py package metadata and cache artifact validation checks into named, targetable surfaces while preserving aggregate skills check and the #1397 named surfaces.
- Scope: Issue #1398 only: tools/skills_surface.py package-metadata and cache-artifacts surfaces; aggregate skills validation compatibility; #1397 docs-reference-sync/generated-tree-drift surfaces preserved; Makefile skills aliases; WI-1398 not_applicable suite/progress/review/current carrier; scheduler-owned review/pr-gate/controlled merge/no_release closeout. No #1399 launcher smoke, #1400 docs/evidence convergence, parent #1261 closeout, umbrella #1255 closeout, release/package/demo/runtime behavior changes, generated skills content change, hosted workflow semantic change, permissions change, external-visible behavior, or Round 9+ scope.
- Execution Path: issue #1398 -> branch work/1398-skills-package-cache-checks -> PR #1424 -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1398.md
- Review Entry: .loom/reviews/WI-1398.json
- Validation Entry: git diff --check; tools/skills_surface.py --list-surfaces and targeted docs-reference-sync/generated-tree-drift/package-metadata/cache-artifacts surfaces; Makefile skills aliases; aggregate tools/skills_surface.py check; tools/loom.py skills check; suite inspect/validate for WI-1398; fact-chain/state-check after scheduler activation; PR metadata preflight/readback; hosted checks
- Closing Condition: PR #1424 for #1398 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1398 is closed, and no_release closeout is consumable by #1261/#1255.
- Current Checkpoint: merge
- Current Stop: Scheduler current-head code review for WI-1398 is recorded and allows merge checkpoint consumption for PR #1424; package-metadata and cache-artifacts surfaces remain targetable, #1397 surfaces and aggregate skills validation remain preserved, and no out-of-scope release/demo/runtime/parent closeout work is included.
- Next Step: Run PR gate, consume hosted checks on PR #1424 current head, then controlled merge and post-merge closeout if clean.
- Blockers: None
- Latest Validation Summary: Scheduler pre-review validation passed for WI-1398 current PR #1424 head after carrier activation: git diff --check; python3 tools/skills_surface.py check --list-surfaces; python3 tools/py_compile_clean.py tools/skills_surface.py; targeted skills surfaces docs-reference-sync, generated-tree-drift, package-metadata, and cache-artifacts; aggregate python3 tools/skills_surface.py check; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_flow.py state-check --target . --item WI-1398; shadow-parity closeout and merge_ready; PR #1424 metadata preflight/readback after body refresh; suite inspect pass; suite validate not_applicable with blocking_gaps=[].
- Recovery Boundary: Issue #1398 only. Do not rewrite or regress #1397 docs/reference sync or generated tree drift surfaces; do not implement #1399 launcher smoke, #1400 docs/evidence convergence, parent #1261 closeout, release/package/demo/runtime changes, generated skills content changes, hosted workflow semantics, permissions, external-visible behavior, or Round 9+ scope.
- Current Lane: skills-package-cache-surfaces

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1394 after PR #1426 merged into `main` at 2026-06-10T23:23:45Z with merge commit `dcefb5df64f9fef1d747faeadf1dfda2d0921fc7`; issue #1394 closed at 2026-06-10T23:29:00Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1394 waiting-scheduler-gate report T1394-waiting-scheduler-gate-202606110610, ran current-head review/gate/controlled-merge readback, used Loom reconciliation sync to add closeout comment and close #1394, manually reconciled the native dependency edge #1260 blocked by #1394 after the tool apply path reported unsupported `add_blocked_by`, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1394 adds named npm package validation targets while preserving aggregate package validation; terminal closeout records no_release because no release package, VERSION, tag, GitHub Release, npm publish, package payload content, runtime behavior, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1394: hosted required checks passed on PR #1426 head `d34c5beaf8bb87c40b2d9adf1a95419e52cb4230`; PR #1426 merged at `dcefb5df64f9fef1d747faeadf1dfda2d0921fc7`; issue #1394 closed; reconciliation audit and closeout check pass after native dependency readback; local `fact-chain`, `state-check`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, suite evidence/carrier validation, and `git diff --check` pass or are being revalidated on the closeout-only carrier branch.
- Lane Entry: npm-package-validation-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1398.md
- Dynamic Truth: .loom/progress/WI-1398.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
