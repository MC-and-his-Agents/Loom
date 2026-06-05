# Current Status

## Derived Fact Chain View

- Item ID: WI-1240-1242
- Goal: Implement the first global-cli runtime provider executable support batch for issues #1240, #1241, and #1242.
- Scope: Model global-cli runtime provider in installed-state, make detect/doctor/verify accept no-.loom/bin repositories only when the provider contract is satisfied, classify stale .loom/bin as repairable residue, and report fact-chain/status/story-carrier current entrypoints through global loom commands while preserving repo-local wrapper compatibility. Ownership constraints are limited to #1240/#1241/#1242 implementation, generated runtime parity, demo fixture parity, and current WI/PR carriers. Excludes #1243/#1244 migration repair/fixtures and #1245/#1246 docs/release closeout.
- Execution Path: issues #1240/#1241/#1242 -> branch work/1240-1242-global-cli-runtime-provider -> PR #1327 -> CI/review -> merge to main.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1240-1242.md
- Review Entry: .loom/reviews/WI-1240-1242.json
- Validation Entry: git diff --check; targeted global-cli smoke; py_compile; skills check; demo bootstrap check; PR gate; release judgment.
- Closing Condition: PR #1327 is merge-ready with global-cli provider behavior consistent across installed-state, doctor/verify, fact-chain/status/story-carrier entrypoints, repo-local wrapper compatibility preserved, and release impact recorded for downstream consumption.
- Current Checkpoint: merge checkpoint
- Current Stop: PR #1327 head is refreshed through current carrier/review sync at 5fd3e3041a8a864f767621da5143cbd967f4b385; PR body machine carrier readback resolves Loom Work Item WI-1240-1242 without --work-item, branch/workspace/head match the formal worktree, and state-check confirms WI-1287 is terminal/report-only. Local PR gate is being rerun after aligning current recovery validation summary with the review artifact.
- Next Step: Rerun authenticated local PR gate without --work-item, inspect hosted checks, classify any failures, then proceed to controlled merge and post-merge closeout after gates pass.
- Blockers: None recorded.
- Latest Validation Summary: Passed locally on 2026-06-05 at head 2d9d025039f89421fca0e227989f507fa2dbe80b: python3 .loom/bin/loom_flow.py state-check --target . --item WI-1240-1242 -> pass, WI-1287 terminal carrier is report-only; git diff --check -> pass; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/governance_surface.py src/skills/shared/scripts/governance_surface.py skills/shared/scripts/governance_surface.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py -> py_compile_clean OK (8 files); PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json -> pass generated_at=2026-06-05T11:25:11Z; targeted global-cli smoke -> TARGETED_GLOBAL_CLI_CHECKS_PASS covering no-.loom/bin installed-state/detect/doctor/verify, global fact-chain/status/story entrypoints, stale .loom/bin repairable residue, and malformed provider fail-closed; python3 tools/loom.py fact-chain --target . --json -> pass; python3 .loom/bin/loom_flow.py flow build --target . --item WI-1240-1242 --build-evidence .loom/progress/WI-1240-1242-build-evidence.json -> pass; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1240-1242 -> pass; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --mode blocking -> pass; python3 .loom/bin/loom_flow.py runtime-parity validate --target . -> pass; python3 .loom/bin/loom_flow.py runtime-evidence --target . --item WI-1240-1242 -> pass; review record refreshed at current head with semantic_review_disposition passed. Full tools/check_cli_contract.py remains intentionally not rerun; prior full-contract failure remains classified as environment/carrier-state, not provider behavior.
- Recovery Boundary: Current batch is limited to #1240/#1241/#1242 global-cli runtime provider executable support plus required generated runtime/demo fixture sync. Excludes #1243/#1244 migration repair/fixtures and #1245/#1246 docs/release closeout.
- Current Lane: implementation-validation

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; targeted global-cli smoke; py_compile; skills check; demo bootstrap check; suite validate; suite carrier validate; flow build; PR gate pending for PR #1327
- Lane Entry: implementation-validation

## Sources

- Static Truth: .loom/work-items/WI-1240-1242.md
- Dynamic Truth: .loom/progress/WI-1240-1242.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
