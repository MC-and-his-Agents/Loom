# Current Status

## Derived Fact Chain View

- Item ID: WI-1451
- Goal: Harden Loom repository required-check governance so `.github/workflows/node-installer-pr.yml` always produces a stable PR check context, preserves full gate behavior on relevant path hits, preserves fast success on path misses, and records the explicit live-config/readback boundary for additional required contexts.
- Scope: Issue #1451 only: change `.github/workflows/node-installer-pr.yml` to run on every pull request; move the path filter into the job so the stable job/check name `node-installer-pr` always appears; preserve the existing full installer gate on relevant path hits; preserve fast success on path misses; record the 2026-06-13 live readback that `main` branch protection currently requires `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, and `loom-pr-merge-gate`, while repo rulesets read back as empty; evaluate `root-self-governance` as a required-context candidate and record the explicit boundary that live branch-protection or ruleset mutation is outside this worker scope. Do not mutate live branch protection/rulesets, loosen existing required checks, admin enforcement, strict status checks, PR merge protection, runner permissions, or implement product-level triggered-check aggregation. Do not process #1244/#1461/#1464/#1465, #1245/#1246/#1238, #1255, Round 9/10/11, Deferred roadmap, VERSION/tag/GitHub Release/npm publish/live actions, shared contract/schema/parser/failure vocabulary changes, or raw host merge.
- Execution Path: issue #1451 -> branch `work/1451-required-check-hardening` -> PR for workflow and WI-1451 carriers -> hosted readback proving stable `node-installer-pr` check context on the exact PR head -> scheduler-owned current-head review / PR gate / merge lane -> separately authorized live-config action only if the scheduler decides to add `node-installer-pr` and/or `root-self-governance` to host-enforced required contexts.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1451.md
- Review Entry: .loom/reviews/WI-1451.json
- Validation Entry: `git diff --check`; YAML syntax parse for `.github/workflows/node-installer-pr.yml`; targeted path-hit/path-miss smoke for the workflow diff detector; `python3 tools/loom.py suite inspect --target . --item WI-1451 --json`; `python3 tools/loom.py suite validate --target . --item WI-1451 --json`; `python3 .loom/bin/loom_init.py fact-chain --target .`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 .loom/bin/loom_flow.py review read --target . --item WI-1451`; `python3 .loom/bin/loom_flow.py state-check --target . --item WI-1451`; PR metadata preflight/readback; hosted check readback for the exact PR head.
- Closing Condition: The WI-1451 PR proves the stable hosted context `node-installer-pr` on the current head, records the current live required-context baseline and `root-self-governance` candidate decision, passes local validation and hosted checks, and stops at `waiting-scheduler-gate` for scheduler-owned review/gate plus any separately authorized live-config readback or mutation.
- Current Checkpoint: closed_out
- Current Stop: WI-1451/#1451 terminal closeout consumed PR #1468 controlled merge, issue #1451 closure, no_release decision, required-context readback, and terminal carrier metadata under watcher merge-lane grant watcher-merge-lane-grant-R8-WI-1451-PR1468-202606121815.
- Next Step: None for WI-1451/#1451 terminal closeout after the closeout-only carrier sync is merged/read back and watcher consumes the lane release. Round 9/10/11, Deferred roadmap, release, and sibling issue scope remain separate.
- Blockers: None for WI-1451/#1451 terminal closeout.
- Latest Validation Summary: Post-merge terminal closeout readback: PR #1468 merged at 2026-06-12T18:20:21Z with merge commit b5d925ea0af8b91f5fe296fffa4dbd6361ceff27; issue #1451 closed/completed at 2026-06-12T18:24:07Z after reconciliation sync; origin/main read back at b5d925ea0af8b91f5fe296fffa4dbd6361ceff27; main branch protection required_status_checks reads back strict=true with contexts `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, `loom-pr-merge-gate`, `node-installer-pr`, and `root-self-governance`; repo rulesets remain `[]`; carrier closeout-sync wrote closed_out metadata for issue 1451, PR 1468, target branch main, and evidence locator github:issue/1451#event-closed;github:pr/1468;git:b5d925ea0af8b91f5fe296fffa4dbd6361ceff27. No additional branch protection or ruleset mutation, release/npm/live/VERSION/tag/GitHub Release/npm publish, contract/schema/parser/failure vocabulary change, raw host merge, #1244/#1461/#1464/#1465, #1245/#1246/#1238, #1255 rewrite, Round 9/10/11 product scope, or Deferred roadmap action was performed.
- Recovery Boundary: WI-1451/#1451 terminal closeout only. No further live branch protection/ruleset mutation, governance loosening, controlled-merge product semantic change, triggered-check aggregation, #1244/#1461/#1464/#1465, #1245/#1246/#1238, #1255 rewrite, Round 9/10/11, Deferred roadmap, VERSION/tag/GitHub Release/npm publish/live action, shared contract/schema/parser/failure vocabulary change, raw host merge, or sibling issue scope is included.
- Current Lane: terminal-closeout

## Runtime Evidence

- Run Entry: Scheduler thread `019eb28d-ac3b-7623-8955-12542fa2e08d` consumed watcher merge-lane grant for WI-1451/#1451, merged PR #1468 through the controlled wrapper, reconciled issue #1451 closure, and opened this closeout-only carrier sync.
- Logs Entry: Closeout worksite is `/Users/mc/.codex/worktrees/1451-required-check-hardening/Loom` on branch `work/1451-post-merge-terminal-sync`; the closeout-only diff is limited to WI-1451 progress/status/review/shadow terminal carriers after PR #1468 merge and issue #1451 closure.
- Diagnostics Entry: WI-1451 replaced the historical generic node installer PR context with the stable always-run hosted context `node-installer-pr`; main branch protection now requires the existing five contexts plus `node-installer-pr` and `root-self-governance`, with strict=true and rulesets still empty.
- Verification Entry: Terminal closeout readback confirms PR #1468 merged at 2026-06-12T18:20:21Z with merge commit b5d925ea0af8b91f5fe296fffa4dbd6361ceff27, issue #1451 closed/completed at 2026-06-12T18:24:07Z, branch protection strict=true with required contexts `py-compile`, `demo-bootstrap`, `repo-local-cli`, `loom-check`, `loom-pr-merge-gate`, `node-installer-pr`, and `root-self-governance`, rulesets `[]`, carrier closeout-sync terminal metadata, and no release or forbidden scope action.
- Lane Entry: terminal-closeout

## Sources

- Static Truth: .loom/work-items/WI-1451.md
- Dynamic Truth: .loom/progress/WI-1451.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
