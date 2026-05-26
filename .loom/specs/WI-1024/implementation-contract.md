# Implementation Contract

## Work Item

- Item ID: WI-1024
- GitHub FR: #1014
- GitHub Work Item: #1024
- Downstream Work Items: #1025, #1026, #1027, #1028
- PR: pending

## Allowed Changes

- `docs/methodology/templates/delivery-planning.md`
- `docs/methodology/templates/README.md`
- `.loom/work-items/WI-1024.md`
- `.loom/progress/WI-1024.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json` current item locator only
- `.loom/specs/WI-1024/**`
- `.loom/reviews/WI-1024*.json`

## Forbidden Changes

- No issue-tree-plan template implementation.
- No PR slicing strategy implementation.
- No GitHub Project / Phase / FR / Work Item mapping implementation.
- No skills routing update.
- No task carrier, evidence-map, consistency-analysis, gate-chain, or CLI automation implementation.
- No closure of #1014 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "delivery planning|Phase|FR|Work Item|PR plan|不替代" docs/methodology docs/adoption skills src .loom`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
