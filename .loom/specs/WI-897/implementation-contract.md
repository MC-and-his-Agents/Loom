# WI-897 Implementation Contract

## Owned Paths

- `tools/check_cli_contract.py`
- `docs/evidence/fixtures/legacy-migration-validation-fixtures.json`
- `docs/adoption/cli-first-legacy-migration-playbook.md`
- `docs/evidence/validations/validation-legacy-migration-release-judgment.md`
- `.loom/work-items/WI-897.md`
- `.loom/progress/WI-897.md`
- `.loom/reviews/WI-897.json`
- `.loom/reviews/WI-897.spec.json`
- `.loom/specs/WI-897/spec.md`
- `.loom/specs/WI-897/plan.md`
- `.loom/specs/WI-897/implementation-contract.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Required Validation

- `python3 tools/check_cli_contract.py`
- `python3 tools/version_surface_check.py`
- `npm --prefix packages/loom-installer run check:versions`
- `npm --prefix packages/loom-installer run check:payload`
- `npm --prefix packages/loom-installer run check:distribution`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-897`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py pr-gate check --target . --pr <PR> --head-sha <HEAD> --item WI-897`
- `make check`

## Merge Contract

- PR body must bind `WI-897` to the branch, worktree, PR, and head SHA.
- PR body may close #897 and #948-#952 only after this evidence is merged or
  merge-ready.
- PR body must leave #996 and #885 open for release readiness and phase closeout.
- #897 records no-publish evidence only; final publish or no-publish judgment
  remains owned by #996.
