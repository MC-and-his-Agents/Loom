# Current Status

## Derived Fact Chain View

- Item ID: WI-1321
- Goal: Implement issue #1321 governance intensity metadata carrier so Loom PR metadata/carrier exposes a minimal consumable governance intensity judgment bound to Work Item, branch/worktree, PR body, head_sha, suite/not_applicable, review, release/no-release and closeout evidence.
- Scope: Allowed: metadata schema, PR body parser/consumer, carrier read/write surfaces, review artifact/PR metadata/head consistency read face, necessary runtime copy sync, targeted fixtures/tests, Loom carrier/status/review/closeout evidence. Excluded: full docs-governance light gate strategy for #1322, full escalation/abuse fixture matrix for #1323, parent closeout #1324, unrelated runtime provider/review engine/merge strategy changes.
- Execution Path: issue #1321 -> branch work/1321-governance-intensity-metadata-carrier -> PR -> metadata parser/fixtures -> review/current-head binding -> pr-gate -> controlled merge -> post-merge closeout consumed.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1321.md
- Review Entry: .loom/reviews/WI-1321.json
- Validation Entry: git diff --check; py_compile_clean; pr metadata-preflight; tools/check_cli_contract.py --surface aggregate; fact-chain; suite validate not_applicable; pr-gate dry check; hosted checks; controlled merge; closeout sync.
- Closing Condition: PR is merged through the controlled merge wrapper, issue #1321 is closed, repo carriers terminalize WI-1321 closeout, and follow-up #1322/#1323/#1324 remain separate.
- Current Checkpoint: merge
- Current Stop: Implementation build, demo fixture sync, fresh review carrier, PR body readback, governance intensity metadata preflight, fact-chain, suite not_applicable validation, and source contract-only loom_check have passed for PR #1351 head 24e4e82d4e27083dae82d0d81f6f473942e5d724.
- Next Step: Rerun local pr-gate against PR #1351 head 24e4e82d4e27083dae82d0d81f6f473942e5d724, wait for hosted checks, run controlled merge, and complete post-merge closeout consumed for issue #1321.
- Blockers: None
- Latest Validation Summary: 2026-06-07 local validation passed: git diff --check; python3 tools/py_compile_clean.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py; python3 tools/skills_surface.py check; python3 tools/loom.py skills check --target . --json; python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .github/PULL_REQUEST_TEMPLATE.md --compare-body-file .github/PULL_REQUEST_TEMPLATE.md --json; python3 tools/check_cli_contract.py --surface aggregate passed in 184.79s; python3 tools/loom.py fact-chain --target . --item WI-1321 --json passed; python3 tools/loom.py suite validate --target . --item WI-1321 --json returned not_applicable with no missing inputs/blocking gaps; python3 tools/loom_check.py --profile source --source-surface contract-only . passed; make loom-demo-new-project-check passed after make loom-demo-new-project-sync refreshed examples/new-project fixture.
- Recovery Boundary: WI-1321 owns only governance intensity metadata carrier/schema/parser/template/runtime-copy/targeted-fixture implementation, generated/demo fixture sync, and Loom carriers. Do not implement #1322 docs-governance light gate strategy, #1323 full escalation fixture matrix, #1324 parent closeout, or unrelated runtime provider/review/merge behavior.
- Current Lane: merge-ready-gate-consumption

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: WI-1321 merge-ready evidence is local and pre-hosted: git diff --check; py_compile_clean; skills surface; skills check; PR metadata preflight/readback for PR #1351 head 24e4e82d4e27083dae82d0d81f6f473942e5d724; tools/check_cli_contract.py --surface aggregate; fact-chain; suite validate not_applicable; loom_check source contract-only; demo bootstrap fixture check.
- Lane Entry: merge-ready-gate-consumption

## Sources

- Static Truth: .loom/work-items/WI-1321.md
- Dynamic Truth: .loom/progress/WI-1321.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
