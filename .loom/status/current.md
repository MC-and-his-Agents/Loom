# Current Status

## Derived Fact Chain View

- Item ID: WI-1125
- Goal: Wire `flow spec-review` and `gate spec-review` to consume `loom suite validate` before spec review approval can pass.
- Scope: #1125 only: update `src/skills/shared/scripts/loom_flow.py`, generated `skills/`, `.loom/bin/`, `.loom/bootstrap/manifest.json`, `src/skills/shared/scripts/loom_check.py`, `docs/methodology/harness/full-spec-suite-cli-surface.md`, and `docs/methodology/harness/cli-command-matrix.md` so spec-review flow/gate and spec-review review-record allow consume suite validation results. Terminalize `.loom/progress/WI-1124.md`. Do not change implementation review semantics except the existing dependency on spec review; do not implement #1126 evidence/carrier/merge-ready checks.
- Execution Path: issue #1125 -> branch work/1125-spec-review-suite-validate -> worktree /Users/mc/dev/Loom-worktrees/1125-spec-review-suite-validate -> PR #1170
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1125.md
- Review Entry: .loom/reviews/WI-1125.json
- Validation Entry: python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1125 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1125 is closed completed, and #1119 can consume the evidence.
- Current Checkpoint: merge
- Current Stop: PR #1170 is open with WI-1125 implementation, validation, spec review, implementation review, and PR metadata recorded.
- Next Step: Pass PR gate, merge PR #1170, and close out #1125.
- Blockers: None
- Latest Validation Summary: Passed: python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py .loom/bin/loom_flow.py .loom/bin/loom_check.py; git diff --check; focused rg for suite_validation, suite-validate, gate spec-review, flow spec-review, /speckit, and .specify surfaces; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom.py suite validate --target . --item WI-1125 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1125; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1125.
- Recovery Boundary: #1125 owns spec-review flow/gate consumption of `loom suite validate` and regression coverage for incomplete formal suite blocking approval. It must not implement #1126 evidence/carrier/merge-ready checks, host writes, merge-ready writes, closeout writes, `/speckit.*`, or `.specify` surfaces.
- Current Lane: full-spec-suite-cli/spec-review-integration

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: Passed: python3 -m py_compile src/skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_check.py skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_check.py .loom/bin/loom_flow.py .loom/bin/loom_check.py; git diff --check; focused rg; python3 tools/skills_surface.py check; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py; python3 tools/check_release_surface.py; python3 tools/version_surface_check.py; python3 tools/check_npm_package.py; python3 tools/host_adapter_check.py; python3 tools/loom.py suite validate --target . --item WI-1125 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1125; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py checkpoint build --target . --item WI-1125.
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1125.md
- Dynamic Truth: .loom/progress/WI-1125.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
