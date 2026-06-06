# Current Status

## Derived Fact Chain View

- Item ID: WI-1269
- Goal: Add the check_cli_contract.py named surface runner with filters, progress/timing, and failure grouping while preserving aggregate behavior.
- Scope: Implement the reusable named surface runner in `tools/check_cli_contract.py`, add optional `--surface` and `--fixture-group` filters plus `--list-surfaces`, report progress/timing, and group failures by surface and fixture group. Preserve full `python3 tools/check_cli_contract.py` aggregate behavior. Excludes #1270-#1274 and #1276-#1280 regression surface splits.
- Execution Path: issue #1269 -> branch work/1269-cli-contract-surface-runner -> PR #1334 -> hosted checks/review -> controlled merge -> post-merge closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1269.md
- Review Entry: .loom/reviews/WI-1269.json
- Validation Entry: python3 tools/py_compile_clean.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface missing; python3 tools/check_cli_contract.py --surface aggregate; PR metadata preflight; hosted checks; controlled merge gate.
- Closing Condition: PR #1334 is merged through controlled merge, issue #1269 is closed, and post-merge closeout consumes PR, issue, branch, head, target-main, review, and validation evidence.
- Current Checkpoint: build
- Current Stop: PR #1334 is open at head b1d085b79587e46fefcbdfc3f1d39062e7fecadb after local validation passed and PR metadata preflight passed; hosted `loom-pr-merge-gate` blocked because the repo fact-chain still pointed to WI-1240-1242 before this carrier sync and no authored review record existed for WI-1269.
- Next Step: Record authored review for the current PR head, rerun local PR gate, wait for hosted checks, then execute controlled merge and post-merge closeout for #1269 only.
- Blockers: None
- Latest Validation Summary: Pre-carrier implementation validation on 2026-06-06: `python3 tools/py_compile_clean.py tools/check_cli_contract.py` passed; `python3 tools/check_cli_contract.py --list-surfaces` listed `aggregate	check-cli-contract`; `python3 tools/check_cli_contract.py --surface missing` exited 2 with unknown surface selection failure; `python3 tools/check_cli_contract.py --surface aggregate` passed with `surface=aggregate fixture_group=check-cli-contract` in 193.12s. PR metadata preflight passed for PR #1334 body/readback at head b1d085b79587e46fefcbdfc3f1d39062e7fecadb.
- Recovery Boundary: Do not handle #1270-#1274, #1276-#1280, or unrelated regression surface splits. Do not write `/Users/mc/dev/Loom` main.
- Current Lane: implementation-merge-ready

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: local CLI contract validation; PR #1334 metadata preflight; hosted checks pending; controlled merge pending
- Lane Entry: implementation-merge-ready

## Sources

- Static Truth: .loom/work-items/WI-1269.md
- Dynamic Truth: .loom/progress/WI-1269.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
