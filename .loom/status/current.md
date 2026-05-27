# Current Status

## Derived Fact Chain View

- Item ID: WI-1049
- Goal: Define the GitHub task carrier profile mapping for issue, sub-issue, Project item, checklist, repo-local `tasks.md`, external tracker, and `not_applicable` carriers.
- Scope: #1049 GitHub task carrier profile mapping only; update the GitHub profile contract and repo-local carriers. Do not update scenario skills routing (#1050), source/generated skills surface (#1051), drift checks, CLI command surface (#1052), or core #1014-#1019 contracts.
- Execution Path: issue #1049 -> branch work/1049-github-task-carrier-profile -> worktree /Users/mc/dev/Loom-worktrees/1049-github-task-carrier-profile
- Workspace Entry: .
- Recovery Entry: .loom/progress/WI-1049.md
- Review Entry: .loom/reviews/WI-1049.json
- Validation Entry: git diff --check; focused rg checks for GitHub profile / task carrier / sub-issue / Project item / checklist / unique execution entry; focused rg checks for forbidden use / review / merge-ready / closeout / provenance / locator; focused rg checks for Project Status / Todo / In Progress / Done / completed truth / host agent; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Closing Condition: #1049 defines GitHub task carrier profile mapping and closes after PR merge, closeout evidence comment, issue closed, and Project status reconciled.
- Current Checkpoint: merge-ready
- Current Stop: PR #1103 opened for WI-1049 with local validation passed; remote PR gate requires Work Item binding update.
- Next Step: Push Work Item / status / review carriers, update PR body with `Loom Work Item: WI-1049`, wait for remote checks, merge, then close #1049.
- Blockers: None recorded.
- Latest Validation Summary: Passed locally on branch `work/1049-github-task-carrier-profile`: `git diff --check`; focused `rg` for GitHub profile / task carrier / sub-issue / Project item / checklist / unique execution entry; focused `rg` for forbidden use / review / merge-ready / closeout / provenance / locator; focused `rg` for Project Status / Todo / In Progress / Done / completed truth / host agent; `python3 tools/skills_surface.py check`; `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Recovery Boundary: #1049 owns GitHub task carrier profile mapping only. Do not update scenario skill routing, source/generated skills surface, drift checks, CLI command surface, or core #1014-#1019 contracts in this Work Item.
- Current Lane: github-task-carrier-profile

## Runtime Evidence

- Run Entry: not_applicable
- Logs Entry: not_applicable
- Diagnostics Entry: not_applicable
- Verification Entry: git diff --check; focused rg checks for GitHub profile / task carrier / sub-issue / Project item / checklist / unique execution entry; focused rg checks for forbidden use / review / merge-ready / closeout / provenance / locator; focused rg checks for Project Status / Todo / In Progress / Done / completed truth / host agent; python3 tools/skills_surface.py check; python3 tools/loom_check.py --profile source --source-surface contract-only .
- Lane Entry: not_applicable

## Sources

- Static Truth: .loom/work-items/WI-1049.md
- Dynamic Truth: .loom/progress/WI-1049.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
