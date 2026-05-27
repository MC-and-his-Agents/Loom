# WI-1051 Implementation Contract

## Work Item

- GitHub Phase: #1012
- GitHub FR: #1020
- GitHub Work Item: #1051
- Upstream Work Items: #1016, #1017, #1018, #1019, #1049, #1050
- Consumed Deferred Work: #1036
- Downstream Work Items: #1020 closeout, #1012 closeout

## Owned Files

- `tools/skills_surface.py`
- `src/skills/install-layout.json`
- `src/skills/route-matrix.md`
- `src/skills/loom-init/SKILL.md`
- `src/skills/loom-spec-review/SKILL.md`
- `src/skills/loom-build/SKILL.md`
- `src/skills/loom-pre-review/SKILL.md`
- `src/skills/loom-merge-ready/SKILL.md`
- `src/skills/shared/references/templates/spec-suite.md`
- `src/skills/shared/references/templates/execution-breakdown.md`
- `src/skills/shared/references/harness/task-carrier-contract.md`
- `src/skills/shared/references/templates/evidence-map.md`
- `src/skills/shared/references/templates/consistency-analysis.md`
- `src/skills/shared/references/templates/scaffold/`
- `skills/`
- `.loom/work-items/WI-1051.md`
- `.loom/progress/WI-1051.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1051/`
- `.loom/reviews/WI-1051.spec.json`
- `.loom/reviews/WI-1051.json`

## Required Outputs

- Source shared references synchronized from docs authority for full suite, linked scaffold templates, execution breakdown, task carrier, evidence-map, and consistency-analysis.
- Scenario skills and route matrix expose installed-state locators for those references.
- `skills_surface.py check` detects docs -> source reference drift and existing source -> generated skills drift.
- Regenerated checked-in `skills/` surface.
- #1036 deferred sync need explicitly consumed in #1051 closeout evidence.

## Forbidden Outputs

- No redefinition of #1014-#1019 core contracts.
- No CLI command surface planning or implementation.
- No new generated-surface authority.
- No closure of #1020 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "full suite|task carrier|evidence-map|consistency-analysis|source/generated|generated skills|drift|deferred|not_applicable" src/skills skills docs/methodology .loom`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/check_release_surface.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
