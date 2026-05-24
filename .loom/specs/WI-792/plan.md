# WI-792 Plan

1. Implement `github-intake issue`, native dependency mirror consumption, source surface selection, and #812 closeout evidence.
2. Sync source, distributed skill, installed demo runtime, and evidence/docs surfaces.
3. Validate focused fixtures, full source profile, installer version gate, pr-gate, and root self-governance.
4. Merge PR #991 to `main`.
5. Reconcile retained #792 children, parent rollups, #812, #792, Project status, and native blocker graph after the merge commit is on `origin/main`.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_check.py`
- `python3 tools/loom_flow.py github-intake issue --target . --issue 794 --phase 792 --fr 793`
- `python3 tools/loom_flow.py flow resume --target . --issue 828`
- `python3 tools/loom_flow.py governance-profile upgrade-plan --target . --host github --issue 833`
- `python3 tools/loom_flow.py reconciliation audit --target . --issue 794 --phase 792 --fr 793`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
- `python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .`
- `python3 tools/loom_check.py --profile source --source-surface distribution-regression .`
- `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- `python3 tools/check_loom_check_runtime_regressions.py`
- `python3 tools/loom_check.py --profile consumer examples/new-project`
- `python3 tools/loom_check.py --profile source .`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `python3 tools/loom_flow.py pr-gate check --target . --pr 991 --head-sha <head> --branch work/792-phase-closeout`
