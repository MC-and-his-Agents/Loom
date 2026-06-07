# Current Status

## Derived Fact Chain View

- Item ID: WI-1322
- Goal: Implement issue #1322 docs-governance lite gate behavior so Loom can consume legal `governance_intensity=light`, `change_class=docs_governance`, `suite_path=not_applicable` PR metadata while keeping review, fact-chain, PR metadata/readback, release/no-release, PR gate, controlled merge, hosted checks, and closeout required.
- Scope: Allowed: suite validate / pr-gate consumption logic for docs-governance lite `not_applicable`, necessary parser/schema behavior, targeted fixtures/tests, minimal PR metadata contract clarification, runtime copy/generated surface synchronization, and WI-1322 Loom carrier/review/status evidence. Excluded: #1323 full escalation and abuse fixture matrix, #1324 parent/final closeout, unrelated runtime provider/review engine/merge/release strategy changes, treating all docs-only changes as docs-governance lite, or fabricating formal suite artifacts to bypass gate.
- Execution Path: issue #1322 -> branch work/1322-docs-governance-lite-gate -> PR -> targeted parser/suite/pr-gate fixtures -> current-head review -> hosted checks -> controlled merge -> post-merge closeout consumed.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1322.md
- Review Entry: .loom/reviews/WI-1322.json
- Validation Entry: git diff --check; py_compile_clean; skills_surface.py check; tools/check_cli_contract.py --surface aggregate; fact-chain; suite validate; pr-gate dry check; hosted checks; controlled merge; closeout sync.
- Closing Condition: PR for #1322 is merged through the controlled merge wrapper, issue #1322 is closed, repo carriers terminalize WI-1322 closeout, and follow-up #1323/#1324 remain separate.
- Current Checkpoint: merge
- Current Stop: Hosted-check failure fixes are locally validated on branch `work/1322-docs-governance-lite-gate`: PR metadata carrier compatibility, demo bootstrap fixture drift, runtime provenance, and shadow parity now pass locally; current local head is still `24f8b4eea956f1f2c853f5288467d09026c054c0` until the fixes are committed.
- Next Step: Commit the refreshed runtime/manifest/shadow fixes, record current-head implementation review against the new head, update PR #1353 metadata/readback, run PR gate dry check, then enter hosted checks.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-07T18:02:30+08:00 local validation passed after hosted-check failure fixes: targeted PR metadata preflight compatibility accepted both review-surface and merge_ready carriers for review consumption; `/usr/bin/python3 .loom/bin/loom_flow.py carrier refresh --target . --dry-run` passed with no refresh needed; `make loom-demo-new-project-check` passed; `/usr/bin/python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking` passed; `make loom-check` passed for source/full profile, 40 source/distribution surfaces, including `pr-metadata-machine`, `root-self-adoption`, `demo-bootstrap`, and `daily-execution-cli`. Pending: commit refreshed fixes, refreshed current-head review, PR body metadata preflight/readback, PR gate dry check against PR head, hosted checks, controlled merge, and closeout sync.
- Recovery Boundary: WI-1322 owns docs-governance lite gate behavior, targeted parser/suite/pr-gate fixtures, minimal contract clarification, runtime copy/generated surface sync, and Loom carriers only. Do not implement #1323 full misuse fixture matrix, #1324 parent/final closeout, unrelated runtime provider/review engine/merge/release strategy, or broad docs-only light-path defaulting.
- Current Lane: docs-governance-lite-gate

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: 2026-06-07T18:02:30+08:00 local validation passed after hosted-check failure fixes: targeted PR metadata preflight compatibility, carrier refresh dry-run, demo bootstrap fixture, shadow parity, and `make loom-check` source/full profile across 40 surfaces; PR metadata/readback, PR gate dry, refreshed current-head review, hosted checks, controlled merge, and closeout remain pending.
- Lane Entry: docs-governance-lite-gate

## Sources

- Static Truth: .loom/work-items/WI-1322.md
- Dynamic Truth: .loom/progress/WI-1322.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
