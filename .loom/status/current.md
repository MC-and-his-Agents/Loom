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
- Current Checkpoint: merge
- Current Stop: PR #1562 is ready for merge gate consumption at head e48ca5ed9ecbc374e68a641d6cb63313902c27a7: wrapper/runtime parameter contract implementation, spec review, implementation review, PR metadata readback, and targeted validation are aligned.
- Next Step: Wait for hosted checks on PR #1562 head e48ca5ed9ecbc374e68a641d6cb63313902c27a7, then run controlled merge only after required checks and Loom merge gate are green.
- Blockers: None
- Latest Validation Summary: 2026-06-17T20:52Z merge-ready carrier readback for PR #1562 head e48ca5ed9ecbc374e68a641d6cb63313902c27a7: PR metadata preflight/readback passed; authored implementation review was refreshed for the current recovery summary; suite evidence/carrier validation passed during review record; local checkpoint merge and PR gate were rerun after removing stale first-slice terminal metadata; targeted CLI validation from 2026-06-17T20:45Z remains unchanged for implementation files.
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
