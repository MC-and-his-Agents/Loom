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
- Current Stop: Repo/global artifact classification contract and adoption/host cross-links are authored on branch `work/1898-repo-global-artifact-contract`; PR #1931 exists; formal suite path is not_applicable; local suite/evidence/carrier/diff validation passed.
- Next Step: Commit suite-path correction, update PR metadata for `suite_path=not_applicable`, then record current-head review evidence.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T05:00:43Z on head 048013880e01923ebda7f5f07a41fb731d1096f3: `python3 tools/loom.py suite validate --target . --item WI-1898 --json` not_applicable; `python3 tools/loom.py suite evidence validate --target . --item WI-1898 --json` pass; `python3 tools/loom.py suite carrier validate --target . --item WI-1898 --json` pass; `git diff --check` pass.
- Recovery Boundary: WI-1898 only freezes repo/global artifact classification. Runtime path resolver, repo carrier implementation, gate independence validation, legacy migration, and release behavior remain separate Work Items.
- Current Lane: repo-global-artifact-contract

## Runtime Evidence

- Run Entry: 2026-07-03T04:40Z WI-1898 work is active in `/Users/mc/dev/Loom` on branch `work/1898-repo-global-artifact-contract`.
- Logs Entry: repo/global artifact classification contract and adoption/host cross-links were authored locally.
- Diagnostics Entry: WI-1898 is a docs-only contract freeze for FR #1897; no runtime path resolver, migration apply, or gate behavior changes are in scope.
- Verification Entry: 2026-07-03T05:00:43Z local validation passed for suite/evidence/carrier and diff hygiene on head 048013880e01923ebda7f5f07a41fb731d1096f3.
- Lane Entry: repo-global-artifact-contract

## Sources

- Static Truth: .loom/work-items/WI-1898.md
- Dynamic Truth: .loom/progress/WI-1898.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
