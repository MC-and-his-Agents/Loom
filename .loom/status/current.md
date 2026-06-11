# Current Status

## Derived Fact Chain View

- Item ID: WI-1407
- Goal: Split tempdir cleanup and demo fixture cleanliness validation into named, targetable runtime regression surfaces while preserving #1405 locking surfaces, #1406 subprocess environment purity, and the aggregate runtime regression entrypoint.
- Scope: Issue #1407 only: `tools/check_loom_check_runtime_regressions.py` tempdir cleanup and demo fixture cleanliness surface registry/selector and stable cleanup/cleanliness diagnostics; Makefile runtime aliases for the two #1407 surfaces; WI-1407 minimal suite/progress/work-item carriers; PR metadata/readback; scheduler-owned review artifacts `.loom/reviews/WI-1407.json` and `.loom/reviews/WI-1407.spec.json`; scheduler-owned shadow evidence `.loom/shadow/merge-ready-loom.json` and `.loom/shadow/closeout-loom.json`; scheduler-owned pr-gate/controlled merge/no_release closeout. Ownership constraints are limited to PR #1444 and WI-1407 repo carriers/review/status/shadow evidence under the watcher-granted lanes. No locking behavior changes, subprocess environment purity rewrite, demo bootstrap generation/drift/canonicalization split under #1262, #1408 aggregate closeout, parent #1263/#1255 closeout, release/package/skills/demo implementation, or external-visible behavior.
- Execution Path: issue #1407 -> branch `work/1407-tempdir-cleanup-fixture-cleanliness` -> PR pending -> scheduler-owned review/pr-gate/controlled merge/no_release closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1407.md
- Review Entry: .loom/reviews/WI-1407.json
- Validation Entry: `git diff --check`; `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`; targeted tempdir cleanup and demo fixture cleanliness runtime targets; existing #1405 locking targets; existing #1406 subprocess-env-purity target; aggregate runtime regression target; py_compile_clean; suite inspect/validate/evidence/carrier validation for WI-1407; residue audit; PR metadata preflight/readback; hosted checks
- Closing Condition: PR for #1407 is reviewed/gated by the scheduler on the current head, merged through the controlled path, issue #1407 is closed, and no_release closeout is consumable by #1263/#1255.
- Current Checkpoint: build
- Current Stop: Scheduler lane grant watcher-lane-grant-R8-WI-1407-202606111731 consumed for WI-1407/#1444 at head 35bbf02f0cd427154d8f5ba338a0a38e91d0e115; current item and review locator are activated for scheduler-owned review/gate.
- Next Step: Author current-head semantic review for PR #1444, refresh shadow/status carriers, run scheduler-owned pr-gate, merge-ready, root-self-governance/high-cost gate path, then request merge_lane if ready.
- Blockers: None
- Latest Validation Summary: Current-head scheduler readback at 00218abea8661b7e43a28617f6729e1efff34924: PR #1444 open/non-draft/mergeable, base 1f760cce1ac48e334800a94f513b3a7173e94d7d; PR body metadata preflight PASS; git diff --check PASS; fact-chain PASS; build checkpoint PASS; suite inspect/validate/evidence/carrier PASS; build evidence integrated; spec review and implementation review are being refreshed for current carrier head; changed files remain limited to WI-1407 runtime regression implementation/docs/carrier/review/shadow/status scope; issue #1407 and parent #1263 remain open.
- Recovery Boundary: Issue #1407 / PR #1444 only under watcher-lane-grant-R8-WI-1407-202606111731. Do not process #1408 until #1407 is merged or aggregate runtime evidence dependency is explicitly satisfied. Do not close parent #1263/#1255, process Round 9/Round 11/deferred roadmap/#1244/#1245/#1246, perform release/npm/live/VERSION/tag/GitHub Release/npm publish actions, or alter shared contract/schema/parser/failure vocabulary outside PR #1444 scope.
- Current Lane: scheduler-review-gate

## Runtime Evidence

- Run Entry: Scheduler consumed watcher closeout extension for WI-1404/#1404 terminal carrier sync after PR #1446 controlled merge and issue #1404 closure.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d owns WI-1404 terminal closeout readback and closeout-only PR request.
- Diagnostics Entry: WI-1404 is docs/evidence convergence for demo bootstrap validation surfaces; it preserves aggregate demo bootstrap validation and does not change validation behavior, fixture content, generated runtime behavior, release/package behavior, workflows, shared parser/schema vocabulary, release execution, or live external state.
- Verification Entry: Terminal closeout readback confirms PR #1446 merged at 2026-06-11T16:35:07Z with merge commit 2983ecb6f4de109c99c73059b67794d2a617377f, issue #1404 closed/completed at 2026-06-11T16:39:53Z, parent #1262 remains open, carrier refresh dry-run passes with refresh_needed=[], fact-chain passes, shadow parity passes for closeout and merge_ready, and git diff check passes. Closeout check blocks only on manual reconciliation findings outside the implementation merge path: forbidden parent native-edge sync and post-merge closeout review evidence classification.
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1407.md
- Dynamic Truth: .loom/progress/WI-1407.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
