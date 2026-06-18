# WI-1533 Plan

## Implementation Steps

1. Add a shared `loom-closeout-specific-gate/v1` payload helper in `loom_flow.py`.
2. Attach the verdict to `gate-freeze --profile closeout` output, including pass, escalation reason, full-review requirement, and next action.
3. Attach the verdict to `pr-gate check --surface closeout` output without affecting ordinary merge-ready PRs.
4. Mark `closeout_specific_gate_profile` as consumed by closeout freeze while leaving `release_no_release_final_closeout` pending for #1515.
5. Extend targeted contract fixtures for passing closeout freeze, release evidence escalation, and terminal closeout PR gate consumption.
6. Sync source, shared, and generated skill runtime copies through `tools/skills_surface.py generate`.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- `git diff --check`
- Suite evidence/carrier validation for WI-1533 after carriers are authored.

## Dependencies

- Hard dependencies consumed: #1532 closeout freeze admission and #1513 failure classifier vocabulary.
- Soft consumers: #1534 docs/skills convergence and #1515 final milestone closeout.
- Related surfaces consumed: #1510 carrier/shadow freshness, #1512 hosted admission, #1541 PR metadata surface, #1554 wrapper/runtime contract, #1555 closeout run.

## Scope Guard

- Implementation ownership is limited to `loom_flow.py` runtime copies, generated runtime parity, targeted CLI contract fixtures, and WI-1533 carriers.
- No docs/skills protocol convergence beyond generated runtime copies.
- No shared truth carrier or GitHub issue/PR body updates except main-thread controlled PR metadata later.
