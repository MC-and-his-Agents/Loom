# Current Status

## Derived Fact Chain View

- Item ID: WI-1898
- Goal: Freeze the repo/global Loom artifact classification contract for global runtime cache migration.
- Scope: Define which Loom artifacts remain repository truth and which workstation-only runtime/tmp/check/artifact payloads may move to ~/.loom/repos/<repo-id>/. Do not implement runtime path resolver, migration apply, or gate behavior changes.
- Execution Path: issue #1898 -> branch work/1898-repo-global-artifact-contract -> PR -> review/merge-ready/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1898.md
- Review Entry: .loom/reviews/WI-1898.json
- Validation Entry: python3 tools/loom.py suite validate --target . --item WI-1898 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1898 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1898 --json; git diff --check
- Closing Condition: Repo/global artifact classification contract is merged, #1898 is closed, and FR #1897 can consume the contract for runtime path resolver and carrier slimdown work.
- Current Checkpoint: review
- Current Stop: Repo/global artifact classification contract and adoption/host cross-links are authored on branch `work/1898-repo-global-artifact-contract`; PR #1931 metadata is current for head e330a5db385ff9be473c6e11b3366460ebf4e4b5; formal suite path is not_applicable; review record passed.
- Next Step: Commit review carrier, refresh PR metadata to the carrier commit, then run merge-ready gate and closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T05:01:28Z on head e330a5db385ff9be473c6e11b3366460ebf4e4b5: `python3 tools/loom.py suite validate --target . --item WI-1898 --json` not_applicable; `python3 tools/loom.py suite evidence validate --target . --item WI-1898 --json` pass; `python3 tools/loom.py suite carrier validate --target . --item WI-1898 --json` pass; `python3 .loom/bin/loom_flow.py fact-chain --target . --item WI-1898` pass; `git diff --check` pass. 2026-07-03T05:03Z `python3 .loom/bin/loom_flow.py flow review --target . --item WI-1898 --issue 1898 --pr 1931 --branch work/1898-repo-global-artifact-contract` pass. 2026-07-03T05:04:42Z `python3 .loom/bin/loom_flow.py review record --target . --item WI-1898 --review-file .loom/reviews/WI-1898.json --decision allow --kind code_review ...` pass.
- Recovery Boundary: WI-1898 only freezes repo/global artifact classification. Runtime path resolver, repo carrier implementation, gate independence validation, legacy migration, and release behavior remain separate Work Items.
- Current Lane: repo-global-artifact-contract

## Runtime Evidence

- Run Entry: 2026-07-03T04:40Z WI-1898 work is active in `/Users/mc/dev/Loom` on branch `work/1898-repo-global-artifact-contract`.
- Logs Entry: repo/global artifact classification contract and adoption/host cross-links were authored locally.
- Diagnostics Entry: WI-1898 is a docs-only contract freeze for FR #1897; no runtime path resolver, migration apply, or gate behavior changes are in scope.
- Verification Entry: 2026-07-03T05:01:28Z local validation passed for suite/evidence/carrier, fact-chain, and diff hygiene on head e330a5db385ff9be473c6e11b3366460ebf4e4b5; 2026-07-03T05:03Z review flow passed with PR #1931 metadata readback; 2026-07-03T05:04:42Z review record passed.
- Lane Entry: repo-global-artifact-contract

## Sources

- Static Truth: .loom/work-items/WI-1898.md
- Dynamic Truth: .loom/progress/WI-1898.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
