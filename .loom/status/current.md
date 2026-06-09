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
- Current Checkpoint: merge
- Current Stop: WI-1282 current-head review is recorded for PR #1385; authorized shadow carriers were refreshed and local gate-input validation is being finalized before commit/push.
- Next Step: Commit the authorized review/shadow carrier correction, run clean-worktree purity/review/pr-gate/metadata validation on the new head, update PR #1385 metadata, read hosted checks, and stop at scheduler-owned gate.
- Blockers: None
- Latest Validation Summary: 2026-06-09 review-shadow correction at PR #1385 head 6fec676e80c8ed631ed4a71a1d9af608679dfbb5: official recovery writeback moved WI-1282 to merge checkpoint; current-head allow review was recorded in .loom/reviews/WI-1282.json after reviewing the frozen repo-local-cli workflow split and WI-1282 carriers; carrier refresh dry-run and write were limited to authorized .loom/shadow/closeout-loom.json and .loom/shadow/merge-ready-loom.json; git diff --check passed; workflow readback confirmed the stable repo-local-cli group order and the 13 preserved commands including setup-demo-bootstrap and runtime-state scene conflict negative check; fact-chain and loom_init verify passed with current item WI-1282; shadow-parity --surface all --blocking passed; adopt verify passed. Pre-commit flow review is expected to purity-block on uncommitted authorized shadow carriers; clean-worktree purity/flow review/pr-gate/PR metadata preflight remain pending after commit.
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
