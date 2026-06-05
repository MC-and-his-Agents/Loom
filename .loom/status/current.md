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
- Current Stop: Latest main through WI-1287 terminal closeout repair is merged into the T3 branch at head 982db36f32f3f2c4275fae8ce2bbd831ea7004e6; current-head implementation review is recorded with semantic_review_disposition passed; state-check confirms WI-1287 is terminal/report-only; local targeted validation is passing. PR #1327 body still needs head readback/update before push/gate.
- Next Step: Update PR #1327 body machine carrier to head 982db36f32f3f2c4275fae8ce2bbd831ea7004e6, run authenticated local PR gate without --work-item, push the branch, inspect hosted checks, classify any failures, then proceed to controlled merge and post-merge closeout.
- Blockers: None recorded.
- Latest Validation Summary: Passed locally on 2026-06-05 at head 982db36f32f3f2c4275fae8ce2bbd831ea7004e6: python3 .loom/bin/loom_flow.py state-check --target . --item WI-1240-1242 -> pass, WI-1287 terminal carrier is report-only; git diff --check -> pass; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/governance_surface.py src/skills/shared/scripts/governance_surface.py skills/shared/scripts/governance_surface.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py -> py_compile_clean OK (8 files); PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json -> pass generated_at=2026-06-05T11:25:11Z; targeted global-cli smoke -> TARGETED_GLOBAL_CLI_CHECKS_PASS covering no-.loom/bin installed-state/detect/doctor/verify, global fact-chain/status/story entrypoints, stale .loom/bin repairable residue, and malformed provider fail-closed; python3 tools/loom.py fact-chain --target . --json -> pass; python3 .loom/bin/loom_flow.py flow build --target . --item WI-1240-1242 --build-evidence .loom/progress/WI-1240-1242-build-evidence.json -> pass; python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-1240-1242 -> pass; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --mode blocking -> pass; python3 .loom/bin/loom_flow.py runtime-parity validate --target . -> pass; python3 .loom/bin/loom_flow.py runtime-evidence --target . --item WI-1240-1242 -> pass; review record refreshed at current head with semantic_review_disposition passed. Full tools/check_cli_contract.py remains intentionally not rerun; prior full-contract failure remains classified as environment/carrier-state, not provider behavior.
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
