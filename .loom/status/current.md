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
- Current Checkpoint: build
- Current Stop: Implementation build validation passed locally after demo fixture sync: governance intensity metadata carrier/schema/parser/template/runtime-copy/targeted fixtures and examples/new-project fixture are ready for PR review.
- Next Step: Record fresh review for the current implementation head, push, update PR body Branch/Head SHA and governance carrier head, rerun PR metadata preflight, pr-gate, hosted checks, controlled merge, and post-merge closeout.
- Blockers: None
- Latest Validation Summary: 2026-06-07 local validation passed: git diff --check; python3 tools/py_compile_clean.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py; python3 tools/skills_surface.py check; python3 tools/loom.py skills check --target . --json; python3 tools/loom.py pr metadata-preflight --surface merge_ready --body-file .github/PULL_REQUEST_TEMPLATE.md --compare-body-file .github/PULL_REQUEST_TEMPLATE.md --json; python3 tools/check_cli_contract.py --surface aggregate passed in 184.79s; python3 tools/loom.py fact-chain --target . --item WI-1321 --json passed; python3 tools/loom.py suite validate --target . --item WI-1321 --json returned not_applicable with no missing inputs/blocking gaps; python3 tools/loom_check.py --profile source --source-surface contract-only . passed; make loom-demo-new-project-check passed after make loom-demo-new-project-sync refreshed examples/new-project fixture.
- Recovery Boundary: WI-1321 owns only governance intensity metadata carrier/schema/parser/template/runtime-copy/targeted-fixture implementation, generated/demo fixture sync, and Loom carriers. Do not implement #1322 docs-governance light gate strategy, #1323 full escalation fixture matrix, #1324 parent closeout, or unrelated runtime provider/review/merge behavior.
- Current Lane: review-refresh-required

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: Post-merge closeout consumed for PR #1347 and issue #1320: hosted checks passed, controlled merge wrapper merged PR #1347, issue #1320 closed with no-release evidence comment, closeout check passed, and terminal carrier metadata is present in `.loom/progress/WI-1320.md`.
- Lane Entry: post-merge-closeout-consumed

## Sources

- Static Truth: .loom/work-items/WI-1321.md
- Dynamic Truth: .loom/progress/WI-1321.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
