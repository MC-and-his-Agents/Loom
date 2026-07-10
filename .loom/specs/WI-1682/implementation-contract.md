# WI-1682 Implementation Contract

## Scope

WI-1682 freezes the first milestone #15 hard dependency contracts:

- governance intensity classification input/output contract
- Work Item / issue / PR / branch / head binding priority
- safe PR metadata repair boundaries
- closeout policy decisions and closeout PR upgrade rules

## Allowed Writes

- `.loom/companion/repo-interface.json`
- `docs/methodology/harness/tiered-gate-consumption-contract.md`
- `docs/methodology/harness/pr-merge-gate.md`
- `docs/methodology/harness/closeout-gate.md`
- `skills/shared/references/harness/pr-merge-gate.md`
- `skills/shared/references/harness/closeout-gate.md`
- `src/skills/shared/references/harness/pr-merge-gate.md`
- `src/skills/shared/references/harness/closeout-gate.md`
- `tools/check_cli_contract.py`
- WI-1682 Loom carriers

## Explicit Non-Goals

- Do not implement `loom ship`.
- Do not change controlled-merge runtime behavior.
- Do not add host mutation behavior.
- Do not publish or prepare v0.18.0 release artifacts in this PR.
- Do not close milestone #15 parent or downstream implementation issues.

## Verification Contract

The PR is valid only when these pass on the current branch:

- `git diff --check`
- `python3 -m json.tool .loom/companion/repo-interface.json`
- `python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/check_cli_contract.py --surface closeout-wrapper`
- `python3 tools/check_cli_contract.py --surface merge-wrapper`
- `python3 tools/check_cli_contract.py --surface controlled-merge`
- `python3 tools/loom.py suite validate --target . --item WI-1682 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1682 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1682 --json`
- `CODEX_EXPORT_GH_TOKEN=1 python3 tools/loom.py pr metadata-preflight 1697 --item WI-1682 --branch work/1682-intensity-binding-closeout-contracts --head-sha <current-head> --json`

## Consumer Boundary

This contract may unblock #1683, #1684, #1687, #1688, #1690, #1691, #1692, and #1694 as a contract dependency. It does not prove those implementation issues complete.
