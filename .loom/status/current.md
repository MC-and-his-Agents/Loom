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
- Current Checkpoint: closed_out
- Current Stop: WI-1407/#1407 terminal closeout consumed PR #1444 controlled merge, issue #1407 closure, no_release decision, and terminal carrier metadata under watcher closeout extension watcher-closeout-extension-R8-WI-1407-202606111756.
- Next Step: None for WI-1407/#1407 terminal closeout. Parent #1263, #1408 aggregate runtime closeout, and umbrella #1255 closeout remain separate scheduler-owned scopes.
- Blockers: None for WI-1407/#1407 terminal closeout.
- Latest Validation Summary: Post-merge terminal closeout readback: PR #1444 merged at 2026-06-11T17:52:22Z with merge commit 4f168c642d95792ed56a15a2347d0e7f8c4bf6f3; issue #1407 closed/completed at 2026-06-11T17:52:24Z; parent #1263 remains open and was not closed out; reconciliation audit classifies only the parent/native dependency edge as outside this grant; carrier closeout-sync wrote closed_out metadata for issue 1407, PR 1444, target branch main, and evidence locator github:issue/1407#event-closed;github:pr/1444;git:4f168c642d95792ed56a15a2347d0e7f8c4bf6f3; no release/npm/live action, workflow/package payload change outside WI-1407/#1444 closeout, shared contract/schema/parser vocabulary change, #1408 processing, or parent closeout was performed.
- Recovery Boundary: WI-1407/#1407 terminal closeout only under watcher decision watcher-closeout-extension-R8-WI-1407-202606111756. Parent #1263 closeout, #1408, #1255, Round 9/11/Deferred, #1244/#1245/#1246, release/npm/live actions, VERSION/tag/GitHub Release/npm publish, workflow/runtime/package payload changes outside WI-1407/#1444 closeout, and shared contract/schema/parser/failure vocabulary remain forbidden.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: Scheduler consumed watcher closeout extension for WI-1407/#1407 terminal carrier sync after PR #1444 controlled merge and issue #1407 closure.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d owns WI-1407 terminal closeout readback and closeout-only PR request.
- Diagnostics Entry: WI-1407 split runtime tempdir cleanup and demo fixture cleanliness validation surfaces while preserving #1405 locking, #1406 subprocess environment purity, and the aggregate runtime regression entrypoint.
- Verification Entry: Terminal closeout readback confirms PR #1444 merged at 2026-06-11T17:52:22Z with merge commit 4f168c642d95792ed56a15a2347d0e7f8c4bf6f3, issue #1407 closed/completed at 2026-06-11T17:52:24Z, parent #1263 remains open, carrier closeout-sync wrote terminal metadata, and this closeout-only branch updates status/progress/task-carrier/review/shadow facts without processing #1408 or parent closeout.
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1407.md
- Dynamic Truth: .loom/progress/WI-1407.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
