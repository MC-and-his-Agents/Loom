# Current Status

## Derived Fact Chain View

- Item ID: WI-1274
- Goal: Split `tools/check_cli_contract.py` adoption/host metadata checks into a named CLI contract surface.
- Scope: Add a stable `adoption-host-metadata` named surface in `tools/check_cli_contract.py` for metadata-only adoption and host metadata verification checks already covered by aggregate `check-cli-contract`. Preserve aggregate behavior except for adding the named surface to surface listing and execution registry. Excludes #1257 parent closeout, #1270-#1273 terminal carriers, Round 5+, Deferred roadmap, release work, hosted workflow changes, metadata schema changes, task-carrier runtime validation semantic changes, and unrelated cleanup.
- Execution Path: issue #1274 -> branch `work/1274-check-cli-adoption-host-metadata-surface` -> implementation validation -> PR metadata/head binding -> hosted checks -> scheduler-owned semantic review, controlled merge, and closeout.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1274.md
- Review Entry: .loom/reviews/WI-1274.json
- Validation Entry: python3 tools/check_cli_contract.py --list-surfaces; python3 tools/check_cli_contract.py --surface adoption-host-metadata; python3 tools/check_cli_contract.py; python3 tools/loom.py fact-chain --target . --json; python3 tools/loom.py suite validate --target . --item WI-1274 --json; python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking; git diff --check; PR metadata preflight/readback; hosted checks.
- Closing Condition: PR for #1274 is reviewed by the scheduler-owned gate, merged through controlled merge, issue #1274 is closed, and post-merge closeout sync consumes PR, issue, branch, target main, review, no-release judgment, hosted checks, and validation evidence.
- Current Checkpoint: closed_out
- Current Stop: WI-1274 is closed out: implementation PR #1370 was merged by the controlled merge wrapper into `main` at merge commit `197556f6d727f3dcf6e6f0d6113c96bfdae867f7`; issue #1274 is closed as COMPLETED; this closeout-only carrier sync consumed the PR, issue, target branch, no-release judgment, hosted checks, and terminal metadata.
- Next Step: No further WI-1274 implementation or closeout work; continue Round 4 with #1257 parent closeout.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-08 post-merge closeout readback for WI-1274: PR #1370 merged through the controlled merge wrapper at 2026-06-08T01:30:24Z with merge commit `197556f6d727f3dcf6e6f0d6113c96bfdae867f7`; issue #1274 closed as COMPLETED at 2026-06-08T01:31:09Z with closeout evidence comment https://github.com/MC-and-his-Agents/Loom/issues/1274#issuecomment-4644775708; final hosted checks for head `d347067f121d2253860dd8cfd10b268129e30877` passed (`py-compile`, `demo-bootstrap`, `repo-local-cli`, `root-self-governance`, `loom-check`, `loom-pr-merge-gate`, and `release-judgment`); `python3 tools/loom.py carrier closeout-sync --target . --item WI-1274 --terminal-state closed_out --issue 1274 --pr 1370 --merge-commit 197556f6d727f3dcf6e6f0d6113c96bfdae867f7 --target-branch main --closed-at 2026-06-08T01:31:09Z --evidence-locator https://github.com/MC-and-his-Agents/Loom/issues/1274#issuecomment-4644775708 --apply --json` passed with `host_mutations=false`.
- Recovery Boundary: Only #1274 adoption-host-metadata surface split and minimal WI-1274 PR-readiness carriers are in scope. Do not touch #1257 parent closeout, #1270-#1273 terminal carriers, Round 5+, Deferred roadmap, release work, hosted workflow changes, metadata schema changes, task-carrier runtime validation semantic changes, or unrelated cleanup.
- Current Lane: check-cli-adoption-host-metadata-surface

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: no blocking diagnostics currently recorded during implementation.
- Verification Entry: post-merge closeout readback passed; PR #1370 merged, issue #1274 closed completed, hosted checks passed, and no release was required
- Lane Entry: check-cli-adoption-host-metadata-surface

## Sources

- Static Truth: .loom/work-items/WI-1274.md
- Dynamic Truth: .loom/progress/WI-1274.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
