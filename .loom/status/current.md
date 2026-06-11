# Current Status

## Derived Fact Chain View

- Item ID: WI-1243
- Goal: Add a safe, reviewable non-mutating migration plan from retained `.loom/bin` compatibility runtime to the `global-cli` runtime provider.
- Scope: `tools/loom.py`, `tools/check_cli_contract.py`, `docs/adoption/loom-installed-state-v2.md`, `docs/adoption/cli-first-legacy-migration-playbook.md`, WI-1243 scoped carriers, `.loom/runtime/build/WI-1243.json`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/reviews/WI-1243.json`, `.loom/reviews/WI-1243.spec.json`, `.loom/shadow/merge-ready-loom.json`, and `.loom/shadow/closeout-loom.json` refreshes required for PR #1437 merge-ready; ownership constraints are limited to these declared #1243 artifacts. In scope are deterministic runtime-carrier migration actions, exact repo-local gate blockers, explicit deletion-confirmation semantics, fixture coverage, and current-head review/gate evidence. Out of scope are #1244/#1245/#1246, Round 8/9/11/Deferred paths, parent #1238/#1246 closeout carriers, unrelated shared contract/schema/parser vocabulary changes, release/npm/live actions, and any mutating repair apply contract.
- Execution Path: issue #1243 -> branch `work/1243-global-cli-runtime-migration-plan` -> worker worktree `/Users/mc/.codex/worktrees/b6f0/Loom` -> PR #1437 -> scheduler-owned review and high-cost gate.
- Workspace Entry: /Users/mc/.codex/worktrees/b6f0/Loom
- Recovery Entry: .loom/progress/WI-1243.md
- Review Entry: .loom/reviews/WI-1243.json
- Validation Entry: git diff --check; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1243 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1243 --json; python3 tools/loom.py pr metadata-preflight 1437 --head-sha <current-head> --surface merge_ready --json
- Closing Condition: PR #1437 for `work/1243-global-cli-runtime-migration-plan` is reviewed, gated, and either merged/read back or explicitly terminalized with deterministic runtime-carrier migration planning, blocker reporting, and non-mutating deletion semantics validated.
- Current Checkpoint: build
- Current Stop: Scheduler consumed watcher lane_grant watcher-lane-grant-1243-202606110946, rebased PR #1437 onto origin/main 500a440320733e97ce107d759fdd188af4518fc5, activated WI-1243 as the current fact-chain item, refreshed WI-1243 evidence-map/scope/build carriers, and is preparing current-head review/shadow/gate inputs for head 6424fb70cbeb1150d7466ba863e8223f158abf3b.
- Next Step: Author WI-1243 current-head spec and implementation review artifacts, refresh shadow parity, run local validation and PR metadata preflight, then push and run scheduler-owned gate/readback. Controlled merge remains a separate merge_lane request after gate/readback.
- Blockers: None
- Latest Validation Summary: Pre-review lane activation readback passed: rebase onto origin/main 500a440320733e97ce107d759fdd188af4518fc5 completed without conflicts; fact-chain/state-check passed for WI-1243 after activation; suite evidence validate passed after evidence-map refresh; build evidence .loom/runtime/build/WI-1243.json records T1243 ownership and scheduler lane integration; carrier refresh reports shadow parity current and review artifact pending.
- Recovery Boundary: Issue #1243 and PR #1437 only. Keep implementation diff scoped to tools/loom.py, tools/check_cli_contract.py, adoption docs, WI-1243 carriers, and watcher-granted current-item/review/shadow carriers. Do not schedule #1244/#1245/#1246, touch Round 8/9/11/Deferred scopes, write parent closeout carriers, execute release/npm/live actions, or perform controlled merge without merge_lane grant.
- Current Lane: runtime-carrier-migration-plan

## Runtime Evidence

- Run Entry: Scheduler consumed T1406 waiting-scheduler-gate report for PR #1433, rebased branch `work/1406-runtime-env-purity-surface` onto `origin/main` `449ba9e672dab6a8c1520806ba2498672cb4c8d8`, resolved the current carrier conflict, added the missing WI-1406 implementation contract, and refreshed local validation on 2026-06-11.
- Logs Entry: Scheduler thread 019eb28d-ac3b-7623-8955-12542fa2e08d owns current-head review, PR gate, controlled merge, and closeout for WI-1406.
- Diagnostics Entry: WI-1406 adds a named subprocess-env-purity runtime regression surface with fixture group `environment-purity` and stable evidence locators while preserving #1405 locking surfaces and aggregate runtime regression validation.
- Verification Entry: Local validation passed on the rebased branch: git diff --check; surface list readback; py_compile_clean; suite inspect/validate/evidence/carrier; make loom-check-runtime-subprocess-env-purity; make loom-check-runtime-locking; make loom-check-runtime-regression; residue audit; skills_surface aggregate check; source contract-only loom_check; check_cli_contract all 6 surfaces. PR metadata, review record, PR gate, controlled merge, and hosted check readback still need refresh after this carrier update and any further head push.
- Lane Entry: runtime-subprocess-env-purity-surface

## Sources

- Static Truth: .loom/work-items/WI-1243.md
- Dynamic Truth: .loom/progress/WI-1243.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
