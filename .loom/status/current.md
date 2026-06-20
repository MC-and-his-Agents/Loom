# Current Status

## Derived Fact Chain View

- Item ID: WI-1484
- Goal: 让流程门禁命令支持摘要与工件化输出，避免 `flow` / gate / scenario 默认路径把完整诊断写入 agent stdout。
- Scope: #1484/#1485 CLI runtime only: wrap global `loom` flow, delegated, scenario, PR gate, merge, reconcile, carrier, and closeout queue command paths with agent-safe stdout and explicit `--full-output`; expose output policy in `loom help --json`; add focused output envelope regression tests. Do not update executable skill text, migration docs, release workflow, package metadata, or downstream repository adoption instructions.
- Execution Path: issues #1484/#1485 -> branch work/1484-1485-cli-agent-safe-output -> PR pending -> hosted gate -> closeout
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1484.md
- Review Entry: .loom/reviews/WI-1484.json
- Validation Entry: python3 test/output_envelope_test.py; python3 -m py_compile tools/loom.py test/output_envelope_test.py; python3 tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata --surface controlled-merge --surface closeout-wrapper; git diff --check
- Closing Condition: PR merges after local/hosted gates prove high-noise global CLI paths default to summary/artifact output, explicit `--full-output` remains available for full JSON diagnostics, and #1478/#1484/#1485 consume the evidence without changing docs/skills/release scope.
- Current Checkpoint: merge
- Current Stop: PR #1665 is open at head d76f067607d1b5f5928a21b159a5f394645ad067 with PR metadata readback passing; implementation contract, review records, suite evidence/carrier validation, fact-chain, and shadow parity have been refreshed locally.
- Next Step: Re-run PR gate and hosted required checks for PR #1665 at head d76f067607d1b5f5928a21b159a5f394645ad067, then merge through controlled path if all gates pass.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-20 local validation passed on branch work/1484-1485-cli-agent-safe-output: python3 test/output_envelope_test.py; python3 -m py_compile tools/loom.py test/output_envelope_test.py; PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata --surface controlled-merge --surface closeout-wrapper; LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES=1024 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py build --target . --item WI-1484 --json returned loom-agent-output-envelope/v1 with artifact locator; LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES=1024 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge-ready --target . --item WI-1484 --json returned loom-agent-output-envelope/v1 with artifact locator; git diff --check.
- Recovery Boundary: CLI runtime output behavior only. Do not update Codex plugin skill text (#1486), documentation/migration text (#1488), release evidence (#1658), or final regression closeout (#1489) in this work item.
- Current Lane: milestone-11-cli-agent-safe-output

## Runtime Evidence

- Run Entry: 2026-06-20 WI-1484/WI-1485 local CLI output wrapper implementation.
- Logs Entry: local command output retained in current Codex milestone/11 thread.
- Diagnostics Entry: High-noise global CLI paths now use agent-safe output envelopes when stdout exceeds budget and keep full JSON behind explicit `--full-output`.
- Verification Entry: `python3 test/output_envelope_test.py`; `python3 -m py_compile tools/loom.py test/output_envelope_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata --surface controlled-merge --surface closeout-wrapper`; `LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES=1024 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py build --target . --item WI-1484 --json`; `LOOM_AGENT_SAFE_STDOUT_BUDGET_BYTES=1024 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py merge-ready --target . --item WI-1484 --json`; `git diff --check`.
- Lane Entry: milestone-11-cli-agent-safe-output

## Sources

- Static Truth: .loom/work-items/WI-1484.md
- Dynamic Truth: .loom/progress/WI-1484.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
