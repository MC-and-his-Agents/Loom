# WI-811 Plan

## Steps

1. Extend `adoption_gate_rollout_status` with `target_mode`, current-mode source, precondition evidence fields, and structured rollback drift conditions.
2. Tighten `loom_check` so blocking is allowed only when every precondition passes with version-controlled evidence.
3. Require rollback coverage for runtime, evidence, host binding, review head, and metadata parsing drift.
4. Update GitHub profile adoption docs, validation evidence, and shared skill references.
5. Regenerate checked-in skill runtime surfaces.
6. Validate with targeted governance-profile commands, py_compile, skills surface, version surface, adoption verification, shadow parity, and full Loom checks.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py governance-profile status --target . --host github`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py governance-profile upgrade-plan --target . --host github`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py governance-profile upgrade --target . --to strong --dry-run --host github`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/governance_surface.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/governance_surface.py skills/shared/scripts/loom_check.py`
- `python3 tools/skills_surface.py check`
- `python3 tools/version_surface_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py adopt verify --target . --item WI-811`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py shadow-parity --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py`
