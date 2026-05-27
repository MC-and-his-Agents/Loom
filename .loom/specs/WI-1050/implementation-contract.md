# WI-1050 Implementation Contract

## Work Item

- GitHub Phase: #1012
- GitHub FR: #1020
- GitHub Work Item: #1050
- Upstream Work Items: #1016, #1018, #1019, #1049
- Downstream Work Items: #1051

## Owned Files

- `src/skills/route-matrix.md`
- `src/skills/loom-story/`
- `src/skills/loom-spec-review/`
- `src/skills/loom-build/`
- `src/skills/loom-pre-review/`
- `src/skills/loom-merge-ready/`
- `src/skills/shared/references/templates/spec-suite.md`
- `skills/`
- `.loom/work-items/WI-1050.md`
- `.loom/progress/WI-1050.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1050/`
- `.loom/reviews/WI-1050.spec.json`
- `.loom/reviews/WI-1050.json`

## Required Outputs

- Scenario skill routing and consumption boundaries for full/minimal suite paths.
- Full path fail-closed wording for missing required artifacts, locators, provenance, evidence freshness, or consistency inputs.
- Minimal path `not_applicable` rationale, consumer boundary, and recheck condition consumption.
- Source and generated skill surface consistency for the changed skill contracts.

## Forbidden Outputs

- No redefinition of #1014-#1019 core contracts.
- No CLI command surface planning or implementation.
- No #1051 drift-check implementation or #1036 closeout from this Work Item.
- No closure of #1020 or #1012 from this Work Item alone.

## Validation

- `git diff --check`
- `rg -n "minimal suite|full suite|suite path|scenario -> validation|acceptance -> test|not_applicable.*recheck condition|consumer boundary" docs/methodology/templates/spec-suite.md src/skills/shared/references/templates/spec-suite.md skills/shared/references/templates/spec-suite.md`
- `rg -n "suite path|full path|minimal path|scenario.*validation|acceptance.*test|not_applicable rationale|consumer boundary|recheck condition|fail-closed" src/skills/route-matrix.md src/skills/loom-story src/skills/loom-spec-review src/skills/loom-build src/skills/loom-pre-review src/skills/loom-merge-ready`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/check_release_surface.py`
- `python3 tools/host_adapter_check.py`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_npm_package.py`
