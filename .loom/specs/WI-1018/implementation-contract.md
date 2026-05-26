# WI-1018 Implementation Contract

## Owned Surface

- `docs/methodology/templates/evidence-map.md`
- `docs/methodology/templates/consistency-analysis.md`
- `docs/methodology/templates/scaffold/evidence-map.md`
- `docs/methodology/templates/scaffold/consistency-analysis.md`
- `docs/methodology/templates/README.md`
- `docs/methodology/templates/spec-suite.md`
- `docs/methodology/harness/status-surface.md`
- `.loom/work-items/WI-1018.md`
- `.loom/progress/WI-1018.md`
- `.loom/specs/WI-1018/*`
- `.loom/reviews/WI-1018*.json`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/progress/WI-1028.md` terminalization only

## Contract Rules

- `evidence-map` is an index and binding contract, not evidence truth.
- `consistency-analysis` outputs findings and remediation direction, not automatic repairs.
- Status surface displays derived evidence / consistency conclusions only.
- #1016 full suite additions are candidate / optional / conditional until #1016 merges.
- #1017 execution breakdown / task carrier inputs are candidate / optional / deferred / not_applicable until #1017 stabilizes.
- #1019 owns gate-chain consumption.
- #1020 owns skills, GitHub profile, and generated surface integration.

## Forbidden Changes

- No skills routing changes.
- No generated skills runtime surface changes.
- No CLI command surface implementation.
- No task carrier truth definition.
- No full suite artifact list definition.

## Validation Contract

- `git diff --check`
- focused `rg` checks
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`

