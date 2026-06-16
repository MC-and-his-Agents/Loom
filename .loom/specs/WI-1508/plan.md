# WI-1508 Plan

## Implementation Steps

1. Add `gate freeze check` and `gate freeze write` to `tools/loom.py` command matrix and route them to the shared flow runtime.
2. Add `gate-freeze check|write` to `src/skills/shared/scripts/loom_flow.py`.
3. Assemble `loom-gate-freeze/v1` from active fact-chain, carriers, PR metadata preflight, review/head binding, shadow parity, suite validation, release judgment, and command surface proof.
4. Keep `check` read-only and restrict `write` to repo-local `.loom/runtime/gate-freeze/<item>.json` artifacts.
5. Sync shared runtime copies and update CLI contract coverage plus command matrix documentation.
6. Record WI-1508 Work Item, progress, spec, plan, implementation contract, evidence map, and task carrier.
7. Run focused local validation and prepare PR metadata/readback for #1508.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py help --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze check --target . --item WI-1508 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py gate freeze write --target . --item WI-1508 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1508 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1508 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1508 --json`
- PR metadata preflight/readback and hosted checks before merge.

## Dependencies

- Parent FR: #1505.
- Hard dependency: #1507 merged and closed.
- Read-only references: `docs/methodology/harness/gate-freeze.md`, #873, #874, #877, #932, #1285.

## Scope Guard

- Do not implement #1509-#1515 behavior in this PR.
- Do not modify `.github/workflows`, PR templates, release workflows, package metadata, VERSION, tags, GitHub Releases, npm state, or external host settings.
