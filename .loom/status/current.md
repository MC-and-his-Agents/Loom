# Current Status

## Derived Fact Chain View

- Item ID: WI-1040
- Goal: Clarify `tasks.md`, GitHub issue/project/checklist, and external tracker replacement boundaries as task carriers.
- Scope: #1040 replacement relationship only; consume #1037-#1039. Do not redefine task carrier core types, implement GitHub Project automation, define evidence-map, change gate-chain, skills routing, or generated skills runtime surface.
- Execution Path: issue #1040 -> branch work/1017-execution-breakdown-task-carrier -> worktree /Users/mc/dev/Loom-1017-execution-breakdown-task-carrier -> PR #1090.
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1040.md
- Review Entry: .loom/reviews/WI-1040.json
- Validation Entry: git diff --check; rg -n "tasks.md|Project done|task done|behavior evidence|test evidence|不替代" docs skills src .loom; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: `tasks.md` is defined as optional carrier, GitHub issue/project/checklist can carry task state but cannot replace Work Item, and task done / Project Done cannot replace behavior evidence, test evidence, review, merge-ready, or closeout.
- Current Checkpoint: validated
- Current Stop: `tasks.md`, GitHub issue/sub-issue, Project item, checklist, and external tracker boundaries are drafted in the task carrier contract and GitHub profile, and validated locally.
- Next Step: Include #1040 and #1017 evidence in the PR, then close out GitHub child issues after merge.
- Blockers: None recorded.
- Latest Validation Summary: Passed after syncing `origin/main` through #1081 merge commit `6c2340763635e9849184a3bd8d241beb783231fe`: `git diff --check`; focused `rg` for `tasks.md`, Project done, task done, behavior evidence, test evidence, Work Item truth, task carrier, execution breakdown, external tracker, checklist, full/minimal spec suite and suite-index boundaries; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py verify --target .`; `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_flow.py purity-check --target . --item WI-1040`; root-self-governance local equivalent (`governance-profile status`, `runtime-parity validate`, `adopt verify`); `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`. The approval remains scoped to the #1017 contract; post-review drift is main-sync/#1081 runtime and terminal carrier-only state, with #1020 integration still deferred.
- Recovery Boundary: #1040 owns carrier replacement boundaries only. Do not implement evidence-map, GitHub automation, gate-chain, skills routing, or generated runtime surface.
- Current Lane: #1017 mainline checkpoint 4 of 4.

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg for execution breakdown, task carrier, Work Item truth, tasks.md, GitHub Project/checklist/external tracker boundaries, behavior evidence, and test evidence; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1040.md
- Dynamic Truth: .loom/progress/WI-1040.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
