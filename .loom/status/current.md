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
- Current Stop: WI-1282 fact-chain activation and required local validation have passed in the worker worksite. Corrective commit/push, PR #1385 metadata refresh, and hosted readback remain before stopping again at scheduler-owned gate.
- Next Step: Commit and push the corrective WI-1282 fact-chain activation head, refresh PR #1385 metadata to the new head, read hosted checks, classify any remaining scheduler-owned gate inputs, then stop at waiting-scheduler-gate.
- Blockers: None
- Latest Validation Summary: 2026-06-09 correction validation on branch work/1282-repo-local-cli-workflow-steps: generated cache cleanup confirmed with git status --porcelain=v1 -uall showing no .loom/bin/__pycache__ residue; activation command python3 .loom/bin/loom_flow.py work-item update --target . --item WI-1282 --activate passed and returned current_fact_chain current_item_id=WI-1282, work_item=.loom/work-items/WI-1282.md, recovery_entry=.loom/progress/WI-1282.md, status_surface=.loom/status/current.md; git diff --check passed; python3 .loom/bin/loom_init.py fact-chain --target . passed with current_item_id WI-1282; python3 .loom/bin/loom_init.py verify --target . passed; python3 tools/loom.py suite validate --target . --item WI-1282 --json returned official result not_applicable with no blocking gaps and expected exit status 1; python3 tools/loom.py suite evidence validate --target . --item WI-1282 --json passed; python3 tools/loom.py suite carrier validate --target . --item WI-1282 --json passed. Workflow step names/order remain unchanged from the frozen command group contract; no semantic review, guardian, controlled merge, issue closeout, #1283/#1284 work, .loom/reviews/**, generated runtime, release/package, or forbidden tool files were written.
- Recovery Boundary: Own only issue #1282. Allowed writes are `.github/workflows/loom-check.yml` for repo-local-cli command group identity/split, `.loom/bootstrap/init-result.json` for WI-1282 fact-chain activation, `.loom/work-items/WI-1282.md` for WI-1282 static truth, `.loom/progress/WI-1282.md`, `.loom/status/current.md`, narrow `.loom/specs/WI-1282/**` evidence carriers, and #1282 PR metadata. Do not edit #1283/#1284/#1259 closeout work, Round 5, Round 7+, release/package workflows, `tools/check_cli_contract.py`, `tools/loom_check.py`, `skills/shared/scripts/loom_check.py`, generated runtime copies, semantic review, guardian, controlled merge, issue closeout, or project/root `/Users/mc/dev/Loom`.
- Current Lane: repo-local-cli-surfaces

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: local command outputs in worker thread 019eabce-a208-72c0-bf67-bc4d51d64857; PR #1385 hosted runs 27199450750 and 27199450775 for pre-activation head `d577d356b6787e86c7cc4251514d3660fb6c2649`; scheduler thread 019eabaf-92dc-7a52-a238-838f4c0bf4ac owns semantic review and gate consumption.
- Diagnostics Entry: WI-1282 activates the repo-local-cli workflow split fact chain for PR #1385. The workflow command group names/order remain frozen; no release/package workflow behavior, runtime CLI semantics, generated runtime files, semantic review artifact, guardian run, controlled merge, or issue closeout is included in this worker correction.
- Verification Entry: `python3 .loom/bin/loom_flow.py work-item update --target . --item WI-1282 --activate` passed and selected WI-1282 as current item. Required corrective validation is tracked in `.loom/progress/WI-1282.md` and must be rerun before commit/push and PR metadata refresh.
- Lane Entry: repo-local-cli-surfaces

## Sources

- Static Truth: .loom/work-items/WI-1282.md
- Dynamic Truth: .loom/progress/WI-1282.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
