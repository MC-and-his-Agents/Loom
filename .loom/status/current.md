# Current Status

## Derived Fact Chain View

- Item ID: WI-1282
- Goal: Split the `repo-local-cli` CI workflow command surface into stable, diagnosable workflow steps while preserving every existing repo-local CLI command, setup dependency, order-sensitive sequence, and the runtime-state scene conflict negative check.
- Scope: Own issue #1282 only: freeze the repo-local-cli command group names/order, split `.github/workflows/loom-check.yml` repo-local-cli step identity, maintain WI-1282 progress/spec/evidence carriers, and refresh PR #1385 metadata for the current head. Excluded: #1283/#1284/#1259 implementation or closeout, Round 5, Round 7+, Deferred roadmap, release/package workflow behavior, `tools/check_cli_contract.py`, `tools/loom_check.py`, `skills/shared/scripts/loom_check.py`, generated runtime copies, semantic review, guardian, controlled merge, and issue closeout.
- Execution Path: issue #1282 -> branch `work/1282-repo-local-cli-workflow-steps` -> freeze command group contract -> split repo-local-cli workflow steps -> preserve command membership/order/setup/negative check -> local validation -> PR #1385 metadata/head binding -> hosted check readback -> scheduler-owned gate.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1282.md
- Review Entry: .loom/reviews/WI-1282.json
- Validation Entry: `git diff --check`; workflow YAML parse and command preservation readback; `make loom-demo-new-project-check`; local split group execution; runtime-state scene conflict negative check; `python3 .loom/bin/loom_init.py fact-chain --target .`; `python3 .loom/bin/loom_init.py verify --target .`; WI-1282 suite/evidence/carrier validation; PR metadata/head readback; hosted check readback.
- Closing Condition: PR #1385 is current-head reviewed and consumed by scheduler-owned gate, then merged; issue #1282 is closed/completed only by scheduler closeout; #1283/#1284/#1259 remain out of this worker scope.
- Current Checkpoint: implementation
- Current Stop: PR #1385 branch is being refreshed from `origin/main` merge `35c1226c676672ad88605db1072409f348e03b8c` after external WI-1280 closeout carrier repair. The expected `.loom/status/current.md` merge conflict was resolved by consuming main's WI-1280 repaired carriers, then reactivating WI-1282 through official Loom tooling.
- Next Step: Finish local validation on the refreshed branch, commit and push the merge/activation head, refresh PR #1385 metadata to the new head, read hosted checks, classify any remaining scheduler-owned gate inputs, then stop at waiting-scheduler-gate.
- Blockers: None
- Latest Validation Summary: 2026-06-09 refresh-main validation in progress on branch work/1282-repo-local-cli-workflow-steps: fetched `origin/main` at `35c1226c676672ad88605db1072409f348e03b8c`, merged it normally, consumed WI-1280 repair files from main unchanged, resolved the expected `.loom/status/current.md` conflict by reactivating WI-1282 with `python3 .loom/bin/loom_flow.py work-item update --target . --item WI-1282 --activate`, and confirmed fact-chain current_item_id=WI-1282. `git diff --check` passed; workflow YAML readback confirmed stable repo-local-cli step order and 13 preserved commands exactly once; `make loom-demo-new-project-check` passed; local split group execution for init-runtime, fact-chain, flow-gates, workspace-locate, and purity-check passed; runtime-state scene conflict negative check failed closed as expected; `python3 .loom/bin/loom_init.py fact-chain --target .` passed with current_item_id WI-1282; `python3 .loom/bin/loom_init.py verify --target .` passed; `python3 tools/loom.py suite validate --target . --item WI-1282 --json` returned official result not_applicable with no blocking gaps and expected exit status 1; `python3 tools/loom.py suite evidence validate --target . --item WI-1282 --json` passed; `python3 tools/loom.py suite carrier validate --target . --item WI-1282 --json` passed. Post-commit purity, PR metadata preflight, push, and hosted readback remain before stopping at scheduler-owned gate. Workflow step names/order remain unchanged from the frozen command group contract; no semantic review, guardian, controlled merge, issue closeout, #1283/#1284 work, `.loom/reviews/WI-1282.json`, generated runtime, release/package, or forbidden tool files were written.
- Recovery Boundary: Own only issue #1282. Allowed writes are `.github/workflows/loom-check.yml` for repo-local-cli command group identity/split, `.loom/bootstrap/init-result.json` for WI-1282 fact-chain activation, `.loom/work-items/WI-1282.md` for WI-1282 static truth, `.loom/progress/WI-1282.md`, `.loom/status/current.md`, narrow `.loom/specs/WI-1282/**` evidence carriers, and #1282 PR metadata. Do not edit #1283/#1284/#1259 closeout work, Round 5, Round 7+, release/package workflows, `tools/check_cli_contract.py`, `tools/loom_check.py`, `skills/shared/scripts/loom_check.py`, generated runtime copies, semantic review, guardian, controlled merge, issue closeout, or project/root `/Users/mc/dev/Loom`.
- Current Lane: repo-local-cli-surfaces

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019eab0f-b79e-7ab1-856e-205b0a288c41
- Diagnostics Entry: `installed-runtime` source surface added through canonical runtime and generated skills sync; no release/package/workflow behavior changes expected.
- Verification Entry: focused `installed-runtime`, `contract-only`, skills parity, compile, and diff checks passed; aggregate `source-self-fixture` consumed and passed `installed-runtime`; non-#1280 `review-run-fixture` residue is classified outside the WI-1280 blocker path.
- Lane Entry: source-self-installed-runtime-fixtures

## Sources

- Static Truth: .loom/work-items/WI-1282.md
- Dynamic Truth: .loom/progress/WI-1282.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
