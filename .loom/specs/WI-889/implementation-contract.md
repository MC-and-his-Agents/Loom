# WI-889 Implementation Contract

## Owned Paths

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `docs/methodology/harness/cli-first-control-plane.md`
- `.loom/work-items/WI-889.md`
- `.loom/progress/WI-889.md`
- `.loom/reviews/WI-889.json`
- `.loom/reviews/WI-889.spec.json`
- `.loom/specs/WI-889/spec.md`
- `.loom/specs/WI-889/plan.md`
- `.loom/specs/WI-889/implementation-contract.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`

## Required Validation

- `python3 tools/check_cli_contract.py`
- `python3 tools/version_surface_check.py`
- `npm --prefix packages/loom-installer run check:versions`
- `npm --prefix packages/loom-installer run check:payload`
- `npm --prefix packages/loom-installer run check:distribution`
- `npm --prefix packages/loom-installer test`
- `make check`
- `python3 .loom/bin/loom_flow.py adopt verify --target . --item WI-889`
- `python3 .loom/bin/loom_flow.py shadow-parity --target .`
- `python3 .loom/bin/loom_flow.py pr-gate check --target . --pr 997 --head-sha <head> --item WI-889`

## Merge Contract

- PR body must include `Loom Work Item: WI-889`.
- PR body must close #889, #892, #896, #910-#914, #924-#928, and #944-#947 only.
- PR body must leave #897 and #996 for their own validation and release-readiness batches.
- Merge is allowed only after implementation review, spec review, merge checkpoint, PR gate, and host checks consume the same PR head.
