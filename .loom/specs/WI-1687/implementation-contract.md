# WI-1687 Implementation Contract

## Runtime Contract

- `pr-metadata render`, `update`, `readback`, and `preflight` accept `--issue`.
- `render` and `update` use the existing PR body artifact path to add or refresh `- Issue: #N`.
- `preflight` blocks a missing issue backlink only when `--issue` is provided.
- A `missing_human_backlink` safe repair action is emitted only after machine carrier preflight passes and host readback or body comparison evidence is available.

## Boundary Contract

- Missing issue backlink repair does not repair Work Item, head, branch, review, release, closeout policy, or machine carrier conflicts.
- Host mutation continues to go through `gh pr edit --body-file`, followed by readback and preflight.
- `--json` payload retains machine-readable evidence and next command.
