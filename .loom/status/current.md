# Current Status

## Derived Fact Chain View

- Item ID: WI-1272
- Goal: Split `tools/check_cli_contract.py` suite carrier checks into a named CLI contract surface.
- Scope: Add a stable `suite-carrier` named surface in `tools/check_cli_contract.py` for suite carrier inspect/validate coverage, including carrier type recognition, normalized statuses, truth boundary, missing/invalid carrier negative fixtures, source locator checks, and existing suite carrier payload assertions. Preserve aggregate `check-cli-contract` behavior. Excludes task-carrier runtime validation semantic changes, suite contract/evidence surface changes except aggregate compatibility, #1273 governance closeout, #1274 adoption/host metadata, #1257 parent closeout, hosted workflow changes, metadata schema changes, release work, and unrelated cleanup.
- Execution Path: issue #1272 -> branch `work/1272-check-cli-suite-carrier-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1272.md
- Review Entry: .loom/reviews/WI-1272.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface suite-carrier; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1272 --json; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1272 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1272 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, no-release judgment, hosted checks, and validation evidence.
- Current Checkpoint: closed_out
- Current Stop: WI-1272 is closed out: implementation PR #1366 was merged by the controlled merge wrapper into `main` at merge commit `d8ee862e125730b26e13b6f13d61c89177712e89`; issue #1272 is closed as COMPLETED; this closeout-only carrier sync consumed the PR, issue, target branch, no-release judgment, hosted checks, and terminal metadata.
- Next Step: No further WI-1272 implementation or closeout work; continue Round 4 with #1273.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-07 post-merge closeout readback for WI-1272: PR #1366 merged through the controlled merge wrapper at 2026-06-07T22:53:36Z with merge commit `d8ee862e125730b26e13b6f13d61c89177712e89`; issue #1272 closed as COMPLETED at 2026-06-07T22:54:08Z with closeout evidence comment https://github.com/MC-and-his-Agents/Loom/issues/1272#issuecomment-4644344121; final hosted checks for head `c8c79ec158c9536b0e9492aae7762c336a928c55` passed (`py-compile`, `demo-bootstrap`, `repo-local-cli`, `root-self-governance`, `loom-check`, `loom-pr-merge-gate`, and `release-judgment`); `python3 tools/loom.py carrier closeout-sync --target . --item WI-1272 --terminal-state closed_out --issue 1272 --pr 1366 --merge-commit d8ee862e125730b26e13b6f13d61c89177712e89 --target-branch main --closed-at 2026-06-07T22:54:08Z --evidence-locator https://github.com/MC-and-his-Agents/Loom/issues/1272#issuecomment-4644344121 --apply --json` passed with `host_mutations=false`.
- Recovery Boundary: Only #1272 suite-carrier surface split and minimal WI-1272 PR-readiness carriers are in scope. Do not implement task-carrier runtime validation semantic changes, #1273, #1274, #1257, Round 5+, release work, hosted workflow changes, metadata schema changes, suite contract/evidence semantic changes, or unrelated cleanup.
- Current Lane: check-cli-suite-carrier-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: no blocking diagnostics currently recorded after local validation.
- Verification Entry: post-merge closeout readback passed; PR #1366 merged, issue #1272 closed completed, hosted checks passed, and no release was required
- Lane Entry: check-cli-suite-carrier-surface

## Sources

- Static Truth: .loom/work-items/WI-1272.md
- Dynamic Truth: .loom/progress/WI-1272.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
