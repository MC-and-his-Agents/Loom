# Current Status

## Derived Fact Chain View

- Item ID: WI-1682
- Goal: Freeze the first hard dependency contracts for milestone #15: governance intensity classification, Work Item/PR binding priority, and closeout policy decisions.
- Scope: Contract documentation, Loom repo metadata contract, and CLI contract fixtures for issues #1682, #1686, and #1695. No runtime behavior, `loom ship` implementation, controlled-merge chaining, release packaging, or hosted workflow changes.
- Execution Path: issues #1682/#1686/#1695 -> branch work/1682-intensity-binding-closeout-contracts -> contract and fixture update -> PR -> controlled merge -> issue closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1682.md
- Review Entry: .loom/reviews/WI-1682.json
- Validation Entry: git diff --check; python3 -m json.tool .loom/companion/repo-interface.json; python3 tools/check_cli_contract.py --surface pr-metadata; python3 tools/check_cli_contract.py --surface closeout-wrapper; python3 tools/check_cli_contract.py --surface merge-wrapper; python3 tools/check_cli_contract.py --surface controlled-merge.
- Closing Condition: PR is merged into main, #1682/#1686/#1695 are closed, and closeout confirms main, PR metadata, issue state, and Loom carriers agree.
- Current Checkpoint: build checkpoint
- Current Stop: Governance intensity classification, binding priority, safe repair, and closeout policy contracts are implemented in docs, repo-interface metadata, skill references, and CLI contract fixtures.
- Next Step: Create PR, refresh review evidence, run PR metadata/gate checks, merge, and close out #1682/#1686/#1695.
- Blockers: None
- Latest Validation Summary: 2026-06-21T15:26Z local validation passed on branch work/1682-intensity-binding-closeout-contracts: python3 tools/skills_surface.py generate; python3 tools/skills_surface.py check; CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py pr metadata-preflight 1697 --item WI-1682 --branch work/1682-intensity-binding-closeout-contracts --head-sha b4e240bacf3b721cce927782d54f9888974b1074 --json; CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1682; python3 tools/check_cli_contract.py --surface governance-closeout. Full python3 tools/check_cli_contract.py passed surfaces 1-11 and reached aggregate, then timed out in pre-review because uncommitted generated payload changes and stale WI-1678 closeout residue still made state-check fall back to admission before this commit. WI-1678 terminal progress/task carrier sync has now been added to this branch so state-check classifies WI-1678 as terminal stale carrier, not an active Work Item.
- Recovery Boundary: WI-1682 owns the first hard dependency contract batch for #1682/#1686/#1695. It does not implement `loom ship`, change controlled merge runtime behavior, create release artifacts, or close milestone #15.
- Current Lane: milestone-15-contract-foundation

## Runtime Evidence

- Run Entry: 2026-06-21 WI-1682 milestone #15 contract foundation in progress.
- Logs Entry: local command output retained in current Codex milestone #15 thread.
- Diagnostics Entry: governance intensity classification, binding priority/safe repair, closeout policy, repo-interface metadata, and contract fixture alignment.
- Verification Entry: `python3 tools/skills_surface.py generate`; `python3 tools/skills_surface.py check`; `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py pr metadata-preflight 1697 --item WI-1682 --branch work/1682-intensity-binding-closeout-contracts --head-sha b4e240bacf3b721cce927782d54f9888974b1074 --json`; `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1682`; `python3 tools/check_cli_contract.py --surface governance-closeout`; partial full `python3 tools/check_cli_contract.py` surfaces 1-11 passed before aggregate pre-review timeout on uncommitted/stale-carrier state.
- Lane Entry: milestone-15-contract-foundation

## Sources

- Static Truth: .loom/work-items/WI-1682.md
- Dynamic Truth: .loom/progress/WI-1682.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
