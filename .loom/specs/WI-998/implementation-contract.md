# WI-998 Implementation Contract

## Owned Paths

- `README.md`
- `README.zh-CN.md`
- `.loom/work-items/WI-998.md`
- `.loom/progress/WI-998.md`
- `.loom/reviews/WI-998.json`
- `.loom/reviews/WI-998.spec.json`
- `.loom/specs/WI-998/spec.md`
- `.loom/specs/WI-998/plan.md`
- `.loom/specs/WI-998/implementation-contract.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Required Validation

- `python3 tools/check_cli_contract.py`
- `python3 tools/version_surface_check.py`
- `npm --prefix packages/loom-installer run check:docs`
- `make check`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-998`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py pr-gate check --target . --pr <PR> --head-sha <HEAD> --item WI-998`

## Merge Contract

- PR body must include `Loom Work Item: WI-998`.
- PR body must close #998 and only reference #885/#996 for consumption.
- #996 must consume the #998 PR, merge commit, and checks before final release judgment.
