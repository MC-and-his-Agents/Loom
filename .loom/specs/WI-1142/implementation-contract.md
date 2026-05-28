# Implementation Contract

- Work Item: WI-1142
- Branch: work/1142-closeout-suite-validation
- Workspace: /Users/mc/dev/Loom-worktrees/1142-closeout-suite-validation
- Authority boundary: closeout suite gate validation is evidence only and must not replace Work Item, review, merge-ready, closeout, Project, reconciliation, or docs/source truth.
- Required local evidence: `tools/check_cli_contract.py`, `git diff --check`, focused `rg`, `tools/skills_surface.py check`, `tools/loom_check.py --profile source --source-surface contract-only .`, suite validate/evidence/carrier validate, build, checkpoint merge, merge-ready, PR gate, closeout.
- Non-goals: no automatic issue close without closeout evidence, no new consistency analyze implementation, no `/speckit.*`, no `.specify/`.
