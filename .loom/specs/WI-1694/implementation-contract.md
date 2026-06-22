# WI-1694 Implementation Contract

## Scope Boundary

- Implementation surface: README, README.zh-CN, source skills, generated skills, plugin skills, WI-1694 carriers, and `tools/check_cli_contract.py` drift guard.
- Runtime surface: unchanged. `tools/loom.py` and `skills/shared/scripts/loom_flow.py` behavior is not modified by WI-1694.
- Release surface: unchanged. Release and milestone closeout remain deferred to #1696.

## Consumer Boundary

- Review may consume this contract as proof that WI-1694 is a documentation / skills / fixture convergence change.
- PR gate and merge-ready may consume it with `.loom/specs/WI-1694/spec.md`, `.loom/specs/WI-1694/plan.md`, `.loom/specs/WI-1694/evidence-map.md`, `.loom/specs/WI-1694/task-carrier.md`, and `.loom/progress/WI-1694-build-evidence.json`.
- Closeout may consume this contract only for WI-1694 scope. It must not treat #1696 release closeout as completed.

## Ownership

- Main executor owns README, source skills, generated skills, plugin skills, fixture integration, and WI-1694 carriers.
- Goodall lane was read-only inventory only and did not author files.

## Validation Contract

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group merge-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1694 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1694 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1694 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1694`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1694`
- `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1694 --build-evidence .loom/progress/WI-1694-build-evidence.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`

## Recheck Conditions

- Re-run the full validation contract if README, `src/skills`, generated skills, plugin skills, `tools/check_cli_contract.py`, or WI-1694 carriers change.
- Create a follow-up Work Item instead of expanding this PR if runtime ship behavior, release publishing, closeout policy semantics, or host mutation behavior needs to change.
