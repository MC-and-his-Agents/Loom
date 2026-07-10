# WI-1544 Plan

## Implementation Steps

1. Add the lane orchestration harness contract.
2. Link the contract from the harness methodology README.
3. Add the shared reference to source skills that consume lane/subagent execution boundaries.
4. Regenerate the skills distribution/runtime copies from `src/skills`.
5. Record WI-1544 fact-chain, review, PR metadata/readback, and focused validation evidence.

## Validation

- `python3 tools/skills_surface.py generate`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/skills_surface.py check --surface package-metadata`
- `python3 tools/skills_surface.py check`
- `git diff --check`
- `python3 tools/loom.py pr metadata-preflight --body-file .loom/tmp/pr-1544-rendered.md --surface merge_ready --json`
- `python3 tools/loom.py pr metadata-preflight 1548 --body-file .loom/tmp/pr-1544-rendered.md --compare-body-file .loom/tmp/pr-1548-readback.md --head-sha 2257d8564494f4a80796541208de9372e114260d --work-item WI-1544 --surface merge_ready --json`

## Dependencies

- Parent FR: #1505.
- Related convergence consumers: #1514, #1534, #1515.
- Hard implementation dependencies: none.

## Scope Guard

- Do not implement #1541, #1542, #1543, #1510, #1512, #1513, #1532, #1533, #1534, or #1515 behavior in this PR.
- Do not modify runtime command behavior, hosted workflows, PR templates, release workflows, package metadata, `VERSION`, tags, GitHub Releases, npm state, or external host settings.
- Do not let subagent output or lane-local evidence author shared truth carriers without main-thread readback and serial write.
