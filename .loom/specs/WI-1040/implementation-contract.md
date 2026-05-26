# WI-1040 Implementation Contract

## Work Item

- Item ID: WI-1040
- Parent FR: #1017
- Upstream WIs: #1037, #1038, #1039
- PR: #1090

## Owned Paths

- `docs/methodology/harness/task-carrier-contract.md`
- `docs/adoption/github-profile.md`
- `docs/methodology/templates/issue-tree-plan.md`
- `docs/methodology/templates/execution-breakdown.md`
- `docs/methodology/templates/spec-suite.md`
- `docs/methodology/harness/work-item-contract.md`
- `docs/methodology/harness/execution-chain.md`
- `docs/methodology/harness/README.md`
- `docs/methodology/templates/README.md`
- `.loom/work-items/WI-1037.md`
- `.loom/work-items/WI-1038.md`
- `.loom/work-items/WI-1039.md`
- `.loom/work-items/WI-1040.md`
- `.loom/progress/WI-1037.md`
- `.loom/progress/WI-1038.md`
- `.loom/progress/WI-1039.md`
- `.loom/progress/WI-1040.md`
- `.loom/specs/WI-1040/*`
- `.loom/reviews/WI-1040*.json`

## Forbidden Paths

- `skills/route-matrix.md`
- `src/skills/route-matrix.md`
- scenario `SKILL.md`
- generated skills runtime surface
- evidence-map / consistency-analysis implementation
- gate-chain implementation
- CLI command surface

## Required Boundaries

- `Work Item` remains the only default execution entry.
- Execution breakdown and task carriers cannot authored recovery dynamic fields.
- `tasks.md` remains optional.
- Carrier `done`, Project `Done`, checklist checked, issue closed, PR merged, and external tracker `Done` cannot replace behavior/test evidence or gate truth.
- #1020 integration needs are recorded but not implemented.

## Validation Commands

- `git diff --check`
- focused `rg` for execution breakdown / task carrier / Work Item truth / `tasks.md` / Project/checklist/external tracker / behavior evidence / test evidence
- `python3 tools/skills_surface.py check`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
