# WI-1049 Implementation Contract

## Work Item

- GitHub Phase: #1012
- GitHub FR: #1020
- GitHub Work Item: #1049
- Upstream Work Items: #1017, #1027
- Downstream Work Items: #1050, #1051

## Owned Files

- `docs/adoption/github-profile.md`
- `.loom/work-items/WI-1049.md`
- `.loom/progress/WI-1049.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1049/`
- `.loom/reviews/WI-1049.json`

## Required Outputs

- GitHub task carrier profile mapping.
- Normalized carrier state rules.
- Host agent Project Status reconciliation rule.
- Repo-local governance carriers and review record.

## Forbidden Outputs

- No scenario skills routing changes.
- No source/generated skills surface synchronization.
- No installer or drift check implementation.
- No CLI command surface planning or implementation.
- No closure of #1020 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "GitHub profile|task carrier|sub-issue|Project item|checklist|唯一执行入口" docs skills src .loom`
- `rg -n "不替代|review|merge-ready|closeout|provenance|locator" docs skills src .loom`
- `rg -n "Project Status|Todo|In Progress|Done|completed truth|host agent" docs skills src .loom`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
