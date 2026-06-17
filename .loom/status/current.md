# Current Status

## Derived Fact Chain View

- Item ID: WI-1554
- Goal: Harden the top-level Loom CLI wrapper to runtime argument contract for high-risk operator gates.
- Scope: First implementation slice for issue #1554: fix `tools/loom.py merge check/run` so the wrapper requires a numeric PR argument, never forwards the literal placeholder `pr` to the runtime `--pr`, and covers that behavior with a focused CLI contract regression surface. Broader `closeout`, `gate closeout`, and `closeout --item` wrapper/runtime contract coverage remains in #1554 follow-up scope.
- Execution Path: issue #1554 -> branch work/1554-cli-wrapper-contract -> merge wrapper PR-number contract -> focused CLI contract surface -> PR metadata/readback -> review/merge-ready
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1554.md
- Review Entry: .loom/reviews/WI-1554.json
- Validation Entry: PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper; PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr; git diff --check
- Closing Condition: This PR is merged, #1554 remains open for the remaining wrapper/runtime contract surfaces, and milestone/12 can consume the merge wrapper bug fix without treating it as final #1554 closeout.
- Current Checkpoint: build
- Current Stop: Merge wrapper PR argument fix and WI-1554 first-slice carriers are implemented on branch `work/1554-cli-wrapper-contract`; targeted validation passed in this worktree.
- Next Step: Update review evidence for the current implementation head, preflight PR metadata, and open a narrow PR that is explicitly `Part of #1554`.
- Blockers: None for the merge wrapper PR argument slice. Remaining #1554 surfaces (`closeout`, `gate closeout`, and `closeout --item`) stay out of this PR and must be handled before #1554 itself can close.
- Latest Validation Summary: 2026-06-17T16:52Z WI-1554 targeted validation passed at implementation head `9fa2f2b54b683011d4a5131711cf0ef82b343d24`: `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1554 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1554 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1554 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr` failed closed in the wrapper with `argument pr-number: invalid int value: 'pr'`; `git diff --check`.
- Recovery Boundary: WI-1554 merge wrapper PR argument slice only. Do not implement retained Work Item parsing (#1494/#1495/#1496), `closeout --item`, `gate closeout`, #1555 one-shot closeout run, hosted admission, classifier taxonomy, closeout freeze profile semantics, release/no-release behavior, or final milestone/12 closeout.
- Current Lane: milestone-12-wi-1554-cli-wrapper-contract

## Runtime Evidence

- Run Entry: 2026-06-18 WI-1554 merge wrapper PR argument implementation slice
- Logs Entry: local command output retained in current Codex thread
- Diagnostics Entry: WI-1554 first slice changes only the merge wrapper PR argument contract and leaves closeout wrapper/runtime surfaces pending under #1554.
- Verification Entry: `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge check pr`; `git diff --check`.
- Lane Entry: milestone-12-wi-1554-cli-wrapper-contract

## Sources

- Static Truth: .loom/work-items/WI-1554.md
- Dynamic Truth: .loom/progress/WI-1554.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
