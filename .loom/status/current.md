# Current Status

## Derived Fact Chain View

- Item ID: WI-1243
- Goal: Add a safe, reviewable non-mutating migration plan from retained `.loom/bin` compatibility runtime to the `global-cli` runtime provider.
- Scope: `tools/loom.py`, `tools/check_cli_contract.py`, `docs/adoption/loom-installed-state-v2.md`, `docs/adoption/cli-first-legacy-migration-playbook.md`, WI-1243 scoped carriers, `.loom/runtime/build/WI-1243.json`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/reviews/WI-1243.json`, `.loom/reviews/WI-1243.spec.json`, `.loom/shadow/merge-ready-loom.json`, and `.loom/shadow/closeout-loom.json` refreshes required for PR #1437 merge-ready; ownership constraints are limited to these declared #1243 artifacts. In scope are deterministic runtime-carrier migration actions, exact repo-local gate blockers, explicit deletion-confirmation semantics, fixture coverage, and current-head review/gate evidence. Out of scope are #1244/#1245/#1246, Round 8/9/11/Deferred paths, parent #1238/#1246 closeout carriers, unrelated shared contract/schema/parser vocabulary changes, release/npm/live actions, and any mutating repair apply contract.
- Execution Path: issue #1243 -> branch `work/1243-global-cli-runtime-migration-plan` -> repo-root workspace `.` -> PR #1437 -> scheduler-owned review and high-cost gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1243.md
- Review Entry: .loom/reviews/WI-1243.json
- Validation Entry: git diff --check; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py; python3 -m py_compile tools/loom.py tools/check_cli_contract.py; python3 tools/loom.py suite validate --target . --item WI-1243 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1243 --json; python3 tools/loom.py pr metadata-preflight 1437 --head-sha <current-head> --surface merge_ready --json
- Closing Condition: PR #1437 for `work/1243-global-cli-runtime-migration-plan` is reviewed, gated, and either merged/read back or explicitly terminalized with deterministic runtime-carrier migration planning, blocker reporting, and non-mutating deletion semantics validated.
- Current Checkpoint: closed_out
- Current Stop: Terminal closeout consumed: PR #1437 was merged by Loom controlled merge at PR head 4d30c0eb9e76a5488053fd77d28cb4dd5c2ea107 with merge commit 16e35be76063a22ba021306ecbafb04bf64e323d; issue #1243 closed at 2026-06-11T11:09:41Z; reconciliation sync, retained merge-ready attempt, hosted required checks, closeout check, shadow parity, and carrier closeout metadata passed.
- Next Step: None for WI-1243. #1244, #1245, #1246, and parent #1238 remain separate work items.
- Blockers: None for WI-1243 terminal closeout.
- Latest Validation Summary: Carrier correction validation passed: python3 .loom/bin/loom_init.py verify --target .; python3 .loom/bin/loom_flow.py governance-profile status --target .; python3 .loom/bin/loom_flow.py runtime-parity validate --target .; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1243; python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run. The workspace profile now reports single-workspace with workspace_entry `.` and no workspace_escape.
- Recovery Boundary: Terminal WI-1243 carrier sync only. Do not reopen implementation, review, PR gate, controlled merge, #1244, #1245, #1246, parent #1238, Round 8/9/11, Deferred scopes, release/npm/live actions, or unrelated shared contract/schema/parser lanes in this closeout carrier update.
- Current Lane: terminal-closeout

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
