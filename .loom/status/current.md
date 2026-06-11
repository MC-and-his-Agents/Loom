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
- Current Checkpoint: closed_out
- Current Stop: WI-1399 terminal closeout facts have been consumed: PR #1432 merged into main at 2026-06-11T05:41:50Z with merge commit 13e1280b24ca0a21be0f602b525038fad1fce96f; issue #1399 closed at 2026-06-11T05:46:25Z; hosted required checks passed on head 60267dc127669a0fc7490976b53310e49e815c02; reconciliation audit passes after adding the native dependency edge #1261 blocked by #1399; no_release terminal metadata is recorded in .loom/progress/WI-1399.md.
- Next Step: None for WI-1399. Skills docs/evidence convergence continues in #1400; parent #1261 and umbrella #1255 consume this closeout later.
- Blockers: None
- Latest Validation Summary: Scheduler validation on PR #1432 head d2277692a38fd1793d3ed37e4a5eb0444b6e525d passed: git diff --check; python3 tools/skills_surface.py check --list-surfaces; python3 tools/skills_surface.py check --surface launcher-smoke --skill loom-init; python3 tools/skills_surface.py check --surface launcher-smoke; make skills-launcher-smoke-check SKILL=loom-init; python3 tools/skills_surface.py check --surface docs-reference-sync; python3 tools/skills_surface.py check --surface generated-tree-drift; python3 tools/skills_surface.py check --surface package-metadata; python3 tools/skills_surface.py check --surface cache-artifacts; python3 tools/skills_surface.py check; python3 tools/loom.py skills check --target . --json; python3 tools/py_compile_clean.py tools/skills_surface.py; python3 tools/loom.py suite inspect --target . --item WI-1399 --json; python3 tools/loom.py suite validate --target . --item WI-1399 --json returned result=not_applicable with blocking_gaps=[] and exit 1 per not_applicable contract; python3 tools/loom_check.py --profile source --source-surface contract-only .; python3 tools/check_cli_contract.py; python3 .loom/bin/loom_init.py fact-chain --target .; python3 .loom/bin/loom_flow.py state-check --target . --item WI-1399; python3 .loom/bin/loom_flow.py flow pre-review --target . --item WI-1399 --issue 1399 --pr 1432 --branch work/1399-skills-launcher-smoke-surface; python3 .loom/bin/loom_flow.py flow review --target . --item WI-1399 --issue 1399 --pr 1432 --branch work/1399-skills-launcher-smoke-surface; GODEBUG=http2client=0 CODEX_EXPORT_GH_TOKEN=1 GH_TOKEN=<gh auth token> python3 .loom/bin/loom_flow.py pr-gate check --target . --item WI-1399 --pr 1432 --head-sha d2277692a38fd1793d3ed37e4a5eb0444b6e525d reached review/metadata pass and fell back only because the current checkpoint was still build. PR #1432 metadata preflight/readback passed for branch work/1399-skills-launcher-smoke-surface and head d2277692a38fd1793d3ed37e4a5eb0444b6e525d.
- Recovery Boundary: WI-1399 is terminal. Do not reopen or modify implementation scope here; #1400, parent #1261, and umbrella #1255 remain separate convergence work.
- Current Lane: skills-launcher-smoke-surface

## Runtime Evidence

- Run Entry: Scheduler closed out WI-1399 after PR #1432 merged into `main` at 2026-06-11T05:41:50Z with merge commit `13e1280b24ca0a21be0f602b525038fad1fce96f`; issue #1399 closed at 2026-06-11T05:46:25Z.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d consumed T1399 waiting-scheduler-gate report T1399-waiting-scheduler-gate-202606110259, ran current-head review/gate/controlled-merge readback, used Loom reconciliation audit and GraphQL `addBlockedBy` to reconcile the native dependency edge #1261 blocked by #1399 after dry-run proof, and recorded terminal no_release closeout metadata.
- Diagnostics Entry: WI-1399 adds a named skills launcher-smoke validation surface with per-skill filtering while preserving #1397 docs-reference-sync/generated-tree-drift, #1398 package-metadata/cache-artifacts, and aggregate skills validation behavior; terminal closeout records no_release because no VERSION, tag, release artifact, package publish, hosted workflow semantics, runtime behavior, permissions, or external-visible behavior was changed.
- Verification Entry: Terminal closeout validation passed for WI-1399: hosted required checks passed on PR #1432 head `60267dc127669a0fc7490976b53310e49e815c02`; PR #1432 merged at `13e1280b24ca0a21be0f602b525038fad1fce96f`; issue #1399 closed; reconciliation audit passes after native dependency readback; local `closeout check`, `fact-chain`, `carrier refresh --dry-run`, `shadow-parity` closeout and merge_ready surfaces, `suite validate` not_applicable with blocking_gaps=[], and `git diff --check` pass on the closeout-only carrier branch.
- Lane Entry: skills-launcher-smoke-surface

## Sources

- Static Truth: .loom/work-items/WI-1399.md
- Dynamic Truth: .loom/progress/WI-1399.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
