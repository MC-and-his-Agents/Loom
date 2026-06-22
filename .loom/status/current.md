# Current Status

## Derived Fact Chain View

- Item ID: WI-1716
- Goal: Expose actionable stale Codex plugin payload refresh guidance from Loom freshness diagnostics.
- Scope: Issue #1716 only. Update `tools/loom.py`, focused CLI contract checks, the Codex user plugin adoption contract, WI-1716 carriers, and WI-1716 spec/code review artifacts. Non-goals: no npm release, no legacy installer behavior, no single SKILL install, no direct writes to Codex-owned runtime cache.
- Execution Path: issue #1716 -> branch `work/1716-plugin-refresh-guidance` -> worktree `.loom/..` -> targeted validation -> PR -> controlled merge -> closeout.
- Workspace Entry: .loom/..
- Recovery Entry: .loom/progress/WI-1716.md
- Review Entry: .loom/reviews/WI-1716.json
- Validation Entry: `python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`; `python3 tools/check_cli_contract.py --surface adoption-host-metadata`; `git diff --check`.
- Closing Condition: PR for `work/1716-plugin-refresh-guidance` is merged into `main`, issue #1716 is closed, and closeout consumes PR, issue, hosted checks, target branch, and repo carrier readback.
- Current Checkpoint: merge
- Current Stop: WI-1716 implementation, targeted validation, spec review, implementation review, review flow, and PR metadata preflight passed for PR #1753; PR gate and hosted checks remain.
- Next Step: Commit merge-checkpoint carrier update, refresh PR metadata for the new head, rerun PR gate, wait for hosted checks, then run controlled merge and closeout for WI-1716.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-23 local checks passed: python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py; python3 tools/check_cli_contract.py --surface adoption-host-metadata; git diff --check; python3 tools/loom.py suite validate --target . --item WI-1716 --json; python3 tools/loom.py suite evidence validate --target . --item WI-1716 --json; python3 tools/loom.py suite carrier validate --target . --item WI-1716 --json; python3 tools/loom.py fact-chain --target . --item WI-1716 --json; LOOM_TEST_NPM_LATEST_VERSION=$(cat VERSION) python3 tools/loom.py upgrade-plan --target . --host codex --json | jq '.actions[] | select(.id == "cli-plugin-freshness")'.
- Recovery Boundary: WI-1716 owns refresh guidance fields, docs, scoped carriers, and scoped review artifacts for stale Codex plugin payload diagnostics. It does not implement broad fixtures (#1717), v0.19.0 release closeout (#1718), legacy installer tombstone behavior (#1732), or v0.20.0 ship friction work (#1735-#1737).
- Current Lane: plugin-refresh-guidance

## Runtime Evidence

- Run Entry: 2026-06-23 WI-1716 build started in issue-scoped worktree `work/1716-plugin-refresh-guidance`.
- Logs Entry: Local validation output is retained in this Codex thread and summarized in `.loom/progress/WI-1716.md`.
- Diagnostics Entry: `loom version --json` and `loom upgrade-plan --target . --host codex --json` expose plugin payload refresh guidance.
- Verification Entry: Targeted CLI contract, py_compile, suite validation, fact-chain, diff checks, and upgrade-plan action readback passed before PR.
- Lane Entry: plugin-refresh-guidance

## Sources

- Static Truth: .loom/work-items/WI-1716.md
- Dynamic Truth: .loom/progress/WI-1716.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
