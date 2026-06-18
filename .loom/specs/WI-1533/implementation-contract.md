# WI-1533 Implementation Contract

- Suite path: minimal

## Contract Surface

- `loom-closeout-specific-gate/v1` is emitted as `closeout_specific_gate`.
- Closeout freeze payloads expose `schema_version`, `source`, `surface`, `mode`, `result`, `verdict`, `closeout_pr_allowed`, `full_review_required`, `escalation_required`, `escalation_reason`, `escalation_reasons`, `blocking_inputs`, and `next_action`.
- Closeout freeze pass returns `verdict == closeout_pr_allowed` and `next_action == closeout_pr_allowed`.
- Closeout freeze block returns a full-review or blocker-resolution verdict with a stable escalation reason.
- Closeout-surface PR gate emits the same schema for terminal closeout carrier PRs.
- Non-closeout `merge_ready` PR gate payloads do not expose `closeout_specific_gate`.

## Consumer Boundary

- #1534 may document the stabilized closeout-specific gate fields after #1533 lands.
- #1515 may read back the field as closeout evidence, but final release/no-release closeout remains out of scope.
- Existing closeout freeze and PR gate pass/block semantics remain authoritative; this contract only adds stable machine-readable verdict fields.

## Non-Goals

- Do not implement #1534 docs/skills convergence.
- Do not implement #1515 final release/no-release closeout.
- Do not change #1555 closeout run orchestration.
- Do not add host writes, issue closure, Project mutation, release/tag/npm publishing, or batch closeout behavior.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- `python3 tools/loom.py suite validate --target . --item WI-1533 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1533 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1533 --json`
