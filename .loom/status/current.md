# Current Status

## Derived Fact Chain View

- Item ID: WI-1271
- Goal: Split `tools/check_cli_contract.py` suite evidence checks into a named CLI contract surface.
- Scope: Add a stable `suite-evidence` named surface in `tools/check_cli_contract.py` for suite evidence inspect/scaffold/validate and evidence-map contract checks while preserving aggregate `check-cli-contract` behavior. Suite carrier inspect/validate assertions remain aggregate-only until #1272. Excludes #1272 suite-carrier follow-up scope, #1273 governance closeout, #1274 adoption/host metadata, #1257 parent closeout, hosted workflow changes, metadata schema changes, release work, and runtime suite semantic changes outside `tools/check_cli_contract.py`.
- Execution Path: issue #1271 -> branch `work/1271-check-cli-suite-evidence-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1271.md
- Review Entry: .loom/reviews/WI-1271.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface suite-evidence; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1271 --json; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1271 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1271 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, and validation evidence.
- Current Checkpoint: closed_out
- Current Stop: WI-1271 is closed out: implementation PR #1362 was merged by the controlled merge wrapper into `main` at merge commit `bddfe6dbb3be406bea2ae79f06bf7b3a6d95e641`; issue #1271 is closed as COMPLETED; this closeout-only carrier sync consumed the PR, issue, target branch, no-release judgment, hosted checks, and terminal metadata.
- Next Step: No further WI-1271 implementation or closeout work; continue Round 4 with #1272.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-07 post-merge closeout readback for WI-1271: PR #1362 merged through the controlled merge wrapper at 2026-06-07T21:15:43Z with merge commit `bddfe6dbb3be406bea2ae79f06bf7b3a6d95e641`; issue #1271 closed as COMPLETED at 2026-06-07T21:16:50Z with closeout evidence comment https://github.com/MC-and-his-Agents/Loom/issues/1271#issuecomment-4644125179; final hosted checks for head `7a8c062eae068d3d0e30766350be3eb863333a1e` passed (`py-compile`, `demo-bootstrap`, `repo-local-cli`, `root-self-governance`, `loom-check`, `loom-pr-merge-gate`, and `release-judgment`); `python3 tools/loom.py carrier closeout-sync --target . --item WI-1271 --terminal-state closed_out --issue 1271 --pr 1362 --merge-commit bddfe6dbb3be406bea2ae79f06bf7b3a6d95e641 --target-branch main --closed-at 2026-06-07T21:16:50Z --evidence-locator https://github.com/MC-and-his-Agents/Loom/issues/1271#issuecomment-4644125179 --apply --json` passed with `host_mutations=false`.
- Recovery Boundary: Only #1271 suite-evidence surface split and minimal WI-1271 PR-readiness carriers are in scope. Do not implement #1272, #1273, #1274, #1257 parent closeout, Round 5+, release work, hosted workflow changes, metadata schema changes, runtime suite semantic changes outside `tools/check_cli_contract.py`, or unrelated cleanup.
- Current Lane: check-cli-suite-evidence-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: no blocking diagnostics remain; #1271 closeout consumed implementation PR #1362, controlled merge readback, issue closure, no-release judgment, and terminal carrier metadata.
- Verification Entry: post-merge closeout readback, carrier closeout-sync apply output, final hosted check readback, and shadow parity for the #1271 closeout carrier PR
- Lane Entry: check-cli-suite-evidence-surface

## Sources

- Static Truth: .loom/work-items/WI-1271.md
- Dynamic Truth: .loom/progress/WI-1271.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
