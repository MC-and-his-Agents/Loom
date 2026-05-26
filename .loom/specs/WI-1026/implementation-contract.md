# WI-1026 Implementation Contract

## Work Item

- GitHub Phase: #1012
- GitHub FR: #1014
- GitHub Work Item: #1026
- Upstream Work Items: #1024, #1025
- Downstream Work Items: #1027, #1028

## Owned Files

- `docs/methodology/templates/pr-slicing.md`
- `docs/methodology/templates/scaffold/pr-slicing.md`
- `docs/methodology/templates/README.md`
- `.loom/work-items/WI-1026.md`
- `.loom/progress/WI-1026.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1026/`
- `.loom/reviews/WI-1026.spec.json`
- `.loom/reviews/WI-1026.json`

## Required Outputs

- PR slicing contract.
- PR slicing scaffold template.
- Templates README registration.
- Repo-local governance carriers and review records.

## Forbidden Outputs

- No PR gate or merge-ready implementation.
- No GitHub Project / Phase / FR / Work Item mapping implementation.
- No skills routing changes.
- No task carrier contract changes.
- No CLI automation.
- No closure of #1014 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "PR slicing|scope purity|single PR|multiple Work Item|review risk|依赖顺序" docs .github skills src .loom`
- `rg -n "Loom Work Item|PR body|merge-ready|review evidence" docs .github skills src .loom`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
