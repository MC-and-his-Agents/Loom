# Current Status

## Derived Fact Chain View

- Item ID: WI-1688
- Goal: Compress metadata and gate diagnostics into minimal actionable root CLI output while preserving full machine-readable payloads.
- Scope: `tools/loom.py` agent-safe output helpers, affected wrapper contract tests, output envelope regression tests, and minimal WI-1688 suite carriers. Ownership constraints are limited to `tools/loom.py`, `tools/check_cli_contract.py`, `test/output_envelope_test.py`, `.loom/bootstrap/init-result.json`, `.loom/status/current.md`, `.loom/work-items/WI-1688.md`, `.loom/progress/WI-1688.md`, `.loom/progress/WI-1688-build-evidence.json`, `.loom/reviews/WI-1688.json`, `.loom/reviews/WI-1688.spec.json`, and `.loom/specs/WI-1688/`.
- Execution Path: issue #1688 -> branch `work/1688-minimal-action-feedback` -> focused wrapper/test update -> PR -> controlled merge -> issue closeout.
- Workspace Entry: `/Users/mc/dev/Loom-WI-1688`
- Recovery Entry: `.loom/progress/WI-1688.md`
- Review Entry: `.loom/reviews/WI-1688.json`
- Validation Entry: `test/output_envelope_test.py`; `tools/check_cli_contract.py --surface pr-metadata`; `--surface governance-closeout`; `--surface controlled-merge`; `--surface closeout-wrapper`; `--surface merge-wrapper`.
- Closing Condition: PR is merged into main, issue #1688 is closed, and closeout confirms compact diagnostics, full payload artifact retention, host state, and Loom carriers agree.
- Current Checkpoint: merge
- Current Stop: Implementation, validation, spec review, implementation review, and PR metadata are integrated; PR gate and merge-ready are in progress.
- Next Step: Run PR gate, hosted check readback, merge-ready, controlled merge, and closeout for #1688.
- Blockers: None
- Latest Validation Summary: 2026-06-22 local validation on branch `work/1688-minimal-action-feedback`: `git diff --check`; `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface controlled-merge`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface closeout-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1688 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1688`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1688`; `PYTHONDONTWRITEBYTECODE=1 python3 skills/loom-build/scripts/loom-build.py flow build --target . --item WI-1688 --build-evidence .loom/progress/WI-1688-build-evidence.json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_check.py --profile source --source-surface contract-only`.
- Recovery Boundary: WI-1688 owns compact actionable CLI diagnostics for existing wrapper outputs. It does not implement `loom ship`, closeout policy, release publishing, or host dependency write execution.
- Current Lane: milestone-15-actionable-diagnostics

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1688 milestone #15 compact actionable diagnostics in progress.
- Logs Entry: local command output retained in current Codex milestone #15 thread.
- Diagnostics Entry: Non-passing root CLI wrapper payloads now expose compact actionable findings while retaining full JSON artifacts.
- Verification Entry: 2026-06-22 local validation for diff check, output tests, py compile, pr-metadata, governance-closeout, controlled-merge, closeout-wrapper, merge-wrapper, suite validate, fact-chain, state-check, build flow, skills surface, and source contract-only loom_check.
- Lane Entry: milestone-15-actionable-diagnostics

## Sources

- Static Truth: `.loom/work-items/WI-1688.md`
- Dynamic Truth: `.loom/progress/WI-1688.md`
- Locator Truth: `.loom/bootstrap/init-result.json`
- Fact Chain CLI: `python3 .loom/bin/loom_init.py fact-chain --target .`
