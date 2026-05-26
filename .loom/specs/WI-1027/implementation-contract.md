# WI-1027 Implementation Contract

## Work Item

- GitHub Phase: #1012
- GitHub FR: #1014
- GitHub Work Item: #1027
- Upstream Work Items: #1024, #1025, #1026
- Downstream Work Items: #1028

## Owned Files

- `docs/adoption/github-profile.md`
- `skills/shared/references/adoption/github-profile.md`
- `src/skills/shared/references/adoption/github-profile.md`
- `.loom/work-items/WI-1027.md`
- `.loom/progress/WI-1027.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1027/`
- `.loom/reviews/WI-1027.spec.json`
- `.loom/reviews/WI-1027.json`

## Required Outputs

- GitHub host mapping contract for delivery planning output.
- Synchronized agent-facing reference surfaces.
- Repo-local governance carriers and review records.

## Forbidden Outputs

- No GitHub API automation.
- No task carrier contract changes.
- No skills routing changes.
- No review / merge-ready / closeout gate-chain implementation.
- No CLI automation.
- No closure of #1014 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "Phase|FR|Work Item|Project item|implementation PR|唯一默认执行入口" docs/adoption docs/methodology skills src .loom`
- `rg -n "Project.*不替代|FR.*不直接|locator|provenance" docs/adoption docs/methodology skills src .loom`
- `rg -n "Project Status|Todo|In Progress|Done|completed truth|closeout" docs/adoption docs/methodology skills src .loom`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
