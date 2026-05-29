# Implementation Contract

## Owned Change Surface

- `tools/check_cli_contract.py`
- `skills/shared/scripts/loom_check.py`
- `src/skills/shared/scripts/loom_check.py`
- `.loom/bin/loom_check.py`
- `examples/new-project/.loom/bin/loom_check.py`
- `.loom/work-items/WI-1147.md`
- `.loom/progress/WI-1147.md`
- `.loom/specs/WI-1147/*`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`

## Contract

- The minimal happy path fixture must include valid spec, plan, evidence-map, execution-breakdown, task-carrier, Work Item, and progress carriers.
- The minimal happy path fixture must pass `suite validate`, `suite evidence validate`, and `suite carrier validate`.
- `loom_check` must prove the same minimal happy path before source review-run and installed pre-merge fixture consumption.
- CLI/runtime outputs remain evidence only and must not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
- #1147 must not implement full-path, fail-closed negative, scaffold, generated parity, PR gate, merge-ready, or closeout integration fixtures reserved for later #1145 Work Items.
