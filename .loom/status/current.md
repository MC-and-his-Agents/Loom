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
- Current Stop: Spec and implementation review are recorded, PR #1327 body machine carrier is updated, and branch is pushed at head 2496d2a3d2d58213a3fd11e52f6f2e95e8815054; ready for PR gate and hosted checks.
- Next Step: Run PR gate with authenticated GitHub readback, inspect hosted checks, classify any failures, then report review-ready or blockers to scheduler.
- Blockers: None recorded.
- Latest Validation Summary: Passed locally on 2026-06-05: git diff --check; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py tools/governance_surface.py src/skills/shared/scripts/governance_surface.py skills/shared/scripts/governance_surface.py tools/check_demo_bootstrap_fixture.py -> py_compile_clean OK; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills check --target . --json -> pass generated_at=2026-06-05T06:33:51Z; make loom-demo-new-project-check -> demo bootstrap fixture OK; targeted global-cli smoke -> TARGETED_GLOBAL_CLI_CHECKS_PASS; python3 tools/loom.py suite validate --target . --item WI-1240-1242 --json -> pass generated_at=2026-06-05T06:28:32Z; python3 tools/loom.py suite carrier validate --target . --item WI-1240-1242 --json -> pass generated_at=2026-06-05T06:27:55Z; python3 .loom/bin/loom_flow.py flow build --target . --item WI-1240-1242 --build-evidence .loom/progress/WI-1240-1242-build-evidence.json -> pass generated_at=2026-06-05T06:29:39Z; python3 .loom/bin/loom_flow.py runtime-evidence --target . --item WI-1240-1242 -> pass; python3 tools/loom.py fact-chain --target . --json -> pass. Full tools/check_cli_contract.py remains classified as environment/carrier-state failure because self-repo carrier state consumed terminal WI-1311 and uncommitted carrier purity before WI-1240-1242 carrier sync.
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
