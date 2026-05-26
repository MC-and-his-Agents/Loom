# WI-1025 Implementation Contract

## Work Item

- GitHub Phase: #1012
- GitHub FR: #1014
- GitHub Work Item: #1025
- Upstream Work Item: #1024
- Downstream Work Items: #1026, #1027, #1028

## Owned Files

- `docs/methodology/templates/issue-tree-plan.md`
- `docs/methodology/templates/scaffold/issue-tree-plan.md`
- `docs/methodology/templates/README.md`
- `.loom/work-items/WI-1025.md`
- `.loom/progress/WI-1025.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1025/`
- `.loom/reviews/WI-1025.spec.json`
- `.loom/reviews/WI-1025.json`

## Required Outputs

- Issue-tree-plan contract.
- Issue-tree-plan scaffold template.
- Templates README registration.
- Repo-local governance carriers and review records.

## Forbidden Outputs

- No PR slicing strategy.
- No GitHub Project / Phase / FR / Work Item mapping implementation.
- No skills routing changes.
- No task carrier contract changes.
- No gate-chain or CLI implementation.
- No closure of #1014 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "issue-tree|phase boundary|FR list|Work Item list|deferred|not_applicable|host carrier" docs/methodology docs/adoption skills src .loom`
- `rg -n "不承载执行进度|review.*结论|merge-ready|closeout" docs/methodology docs/adoption skills src .loom`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
