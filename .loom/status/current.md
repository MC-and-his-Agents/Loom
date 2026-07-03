# Current Status

## Derived Fact Chain View

- Item ID: WI-1901
- Goal: Prove Loom doctor, resume, review read, PR gate, and merge-ready do not depend on repo-local `.loom/runtime` or `.loom/tmp` cache directories.
- Scope: Add focused contract coverage under the runtime-paths surface for a target repository whose repo-local runtime/tmp cache is absent while stable Loom truth carriers remain present. Ownership constraints are limited to `tools/check_cli_contract.py`, WI-1901 Loom carriers, and the active fact-chain/status carriers.
- Execution Path: issue #1901 -> branch work/1901-gate-no-repo-local-cache -> PR -> review/merge-ready/closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1901.md
- Review Entry: .loom/reviews/WI-1901.json
- Validation Entry: python3 tools/py_compile_clean.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface runtime-paths; python3 tools/loom.py suite validate --target . --item WI-1901 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1901 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1901 --json; git diff --check
- Closing Condition: Focused cache-absent gate fixture passes, PR is merged, #1901 is closed, and repo carrier closeout is terminalized.
- Current Checkpoint: build
- Current Stop: Focused runtime-paths contract fixture added and initial targeted validation passed locally.
- Next Step: Validate suite carriers, record review, refresh PR metadata, run PR gate, and merge.
- Blockers: None recorded.
- Latest Validation Summary: 2026-07-03T09:44Z on branch work/1901-gate-no-repo-local-cache before final carrier commit, passed `python3 tools/py_compile_clean.py tools/check_cli_contract.py` and `python3 tools/check_cli_contract.py --surface runtime-paths`.
- Recovery Boundary: Continue from WI-1901 branch changes to `tools/check_cli_contract.py` and `.loom/specs/WI-1901/` carriers only.
- Current Lane: cache-absent-gate-contract

## Runtime Evidence

- Run Entry: 2026-07-03T09:44Z WI-1901 focused contract fixture validated in `/Users/mc/dev/Loom` on branch `work/1901-gate-no-repo-local-cache`.
- Logs Entry: Cache-absent fixture deletes target repo-local `.loom/runtime` and `.loom/tmp`, then verifies doctor/resume/review/pr-gate/merge-ready without repo-local cache recreation.
- Diagnostics Entry: WI-1901 changes `tools/check_cli_contract.py` and WI-1901 suite carriers only; workstation orchestration, legacy migration, and release behavior remain out of scope.
- Verification Entry: 2026-07-03T09:44Z local checks passed: py_compile_clean for `tools/check_cli_contract.py` and runtime-paths focused contract.
- Lane Entry: cache-absent-gate-contract

## Sources

- Static Truth: .loom/work-items/WI-1901.md
- Dynamic Truth: .loom/progress/WI-1901.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
