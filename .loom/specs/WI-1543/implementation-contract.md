# WI-1543 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/loom.py` exposes `loom closeout queue status` as an implemented JSON command.
- `src/skills/shared/scripts/loom_flow.py` exposes `closeout-queue status` as the read-only runtime surface used by the top-level CLI.
- The command requires an explicit `--issue`, `--item`, or `--queue-file` before scanning retained Work Items.
- The output schema is `loom-closeout-queue-status/v1` and includes `result`, `mode`, `items`, `mode_counts`, `missing_inputs`, `next_action`, `next_command`, `mutates`, `host_mutations`, and `carrier_mutations`.
- Queue item modes are `auto_no_op`, `light_carrier_sync`, `batched_closeout`, `full_closeout`, and `blocked`.
- Missing target, missing input, and explicit filter miss paths preserve `mutates=false`, `host_mutations=false`, and `carrier_mutations=false`.
- Generated skills runtime copies stay aligned with the canonical shared runtime.
- The CLI command matrix documents the read-only boundary.

## Consumer Boundary

- Review, PR gates, hosted checks, and milestone/12 closeout may consume this contract as a read-only queue/status entrypoint.
- #1532/#1533 may consume the command after merge as an input surface, but this PR does not define closeout freeze admission behavior.
- #1513 may later map queue failures into a broader classifier taxonomy, but this PR does not freeze classifier names beyond local closeout modes.

## Non-Goals

- Do not implement queue apply/sync behavior.
- Do not mutate GitHub issue, PR, Project, release, branch, worktree, or versioned Loom carriers.
- Do not change hosted admission, failure classifier taxonomy, or closeout freeze profile semantics.
- Do not perform final release/no-release closeout.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/loom_flow.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface package-metadata`
- `git diff --check`
