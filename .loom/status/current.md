# Current Status

## Derived Fact Chain View

- Item ID: WI-1554
- Goal: Harden the top-level Loom CLI wrapper to runtime argument contract for high-risk operator gates.
- Scope: Complete issue #1554 remaining wrapper/runtime contract surfaces: keep merge check/run numeric PR argument coverage, forward runtime-supported closeout check parameters from tools/loom.py, and add focused contract coverage for closeout and gate closeout without changing closeout gate semantics or one-shot post-merge closeout orchestration. Write ownership is limited to WI-1554 carriers/specs, `tools/loom.py`, and `tools/check_cli_contract.py`.
- Execution Path: issue #1554 -> branch work/1554-wrapper-closeout-contract -> closeout wrapper/runtime parameter forwarding -> focused merge-wrapper and governance-closeout contract surfaces -> PR metadata/readback -> review/merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1554.md
- Review Entry: .loom/reviews/WI-1554.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout; closeout/gate closeout --item smoke; git diff --check
- Closing Condition: PR #1562 is merged, issue #1554 is closed after closeout evidence confirms merge and closeout wrapper/runtime contract coverage, and #1514/#1534/#1515 can consume #1554 as complete.
- Current Checkpoint: build
- Current Stop: PR #1562 contains the complete #1554 wrapper/runtime contract slice: merge check/run, closeout, and gate closeout wrapper argument contracts are implemented, spec/plan/evidence are aligned, focused validation passed, and build evidence is integrated.
- Next Step: Record current-head implementation review for 90c12dce0d134dc9e398284e2beb2788c5be1e74, update PR #1562 with the carrier/review head, rerun PR metadata preflight and PR gate, then move the PR out of draft when gates are clean.
- Blockers: None
- Latest Validation Summary: 2026-06-17T20:45Z targeted validation passed for PR #1562 head 90c12dce0d134dc9e398284e2beb2788c5be1e74 after spec/plan alignment: PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1554 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1554 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1554 --json; PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface governance-closeout; PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py flow build --target . --item WI-1554 --build-evidence .loom/progress/WI-1554-build-evidence.json consumed integrated build evidence; closeout and gate closeout --item smokes reached closeout check and blocked only on issue is not closed; PR metadata preflight/readback compare passed for PR #1562; git diff --check.
- Recovery Boundary: Current slice is limited to CLI wrapper/runtime parameter contract hardening for #1554. It does not implement #1555 one-shot post-merge closeout run, hosted admission, release/no-release closeout, or closeout gate semantic changes.
- Current Lane: milestone-12-wave0-cli-wrapper-contract

## Runtime Evidence

- Run Entry: 2026-06-17 WI-1510 carrier refresh and shadow freshness freeze input implementation slice
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1510 adds `carrier_refresh` and `shadow_freshness` gate freeze input bindings and keeps closeout terminal profile semantics unchanged.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1510 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1510 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1510 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `git diff --check`.
- Lane Entry: milestone-12-wi-1510-carrier-shadow-freeze

## Sources

- Static Truth: .loom/work-items/WI-1554.md
- Dynamic Truth: .loom/progress/WI-1554.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
