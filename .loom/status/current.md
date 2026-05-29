# Current Status

## Derived Fact Chain View

- Item ID: WI-1144
- Goal: Keep distributed CLI release, version, package, and generated-surface checks aligned after suite automation is added.
- Scope: #1144 only: make root `loom` package checks require suite source-truth docs, make `loom skills release-check` consume package dry-run validation, add focused contract/smoke assertions, and consume #1143 terminal carrier truth after PR #1182 merge. Do not refactor unrelated packaging or publish workflows.
- Execution Path: issue #1144 -> branch work/1144-release-version-package-surface -> worktree /Users/mc/dev/Loom-worktrees/1144-release-version-package-surface -> PR pending.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1144.md
- Review Entry: .loom/reviews/WI-1144.json
- Validation Entry: python3 tools/check_npm_package.py; python3 tools/loom.py skills release-check --json; node --test test/npm-package-smoke.test.mjs; python3 tools/check_cli_contract.py; git diff --check; focused rg; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1144 PR is merged to main, closeout evidence records PR/head/merge/target branch/validation/Project state, #1144 is closed completed, and #1136 can consume the evidence.
- Current Checkpoint: merge
- Current Stop: PR #1183 is open at head ee0dabd3 with implementation, spec, review, and release/package validation recorded; merge-ready checkpoint synchronization is in progress.
- Next Step: Pass PR gate, run merge-ready, merge PR #1183, then record #1144 closeout evidence and Project Done state.
- Blockers: None recorded.
- Latest Validation Summary: Passed `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_npm_package.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`; `node --test test/npm-package-smoke.test.mjs`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`; `git diff --check`; focused `rg` for package/release-check docs and forbidden external command/layout strings; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only .`; `make loom-demo-new-project-check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1144 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1144 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1144 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py state-check --target . --item WI-1144`; and `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`. Also reconciled #1143 terminal carrier truth after PR #1182 merge.
- Recovery Boundary: #1144 owns release/version/package/generated-surface checks only; it must not change publish workflow semantics, version authority, host truth, review truth, merge-ready truth, or closeout truth.
- Current Lane: full-spec-suite-cli/release-version-package-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: python3 .loom/bin/loom_init.py verify --target .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1144.md
- Dynamic Truth: .loom/progress/WI-1144.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
