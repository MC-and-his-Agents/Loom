# WI-1543 Plan

## Implementation Steps

1. Add `loom closeout queue status` to the CLI command matrix and route it to a repo-local `closeout-queue status` runtime surface.
2. Implement a read-only closeout queue/status payload that consumes explicit `--issue`, `--item`, or `--queue-file` inputs and refuses broad implicit scans.
3. Parse terminal closeout metadata and optional queue fixtures into host completion evidence.
4. Classify each retained item as `auto_no_op`, `light_carrier_sync`, `batched_closeout`, `full_closeout`, or `blocked`.
5. Preserve no-mutation envelope fields across normal, missing-input, filter-miss, and missing-target paths.
6. Add deterministic governance closeout contract fixtures for classification, read-only snapshots, filtered status, input guards, and envelope stability.
7. Regenerate skills runtime copies from `src/skills`.
8. Update the CLI command matrix documentation for the read-only queue/status boundary.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/loom_flow.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface package-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout queue status --target . --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout queue status --target . --item WI-does-not-exist --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout queue status --target /definitely/not/exist --json`
- `git diff --check`

## Dependencies

- Hard dependency #1531 closeout terminal profile contract is already available.
- Consumes #1542 retained Work Item lookup hardening through target branch `origin/main`.
- Soft downstream consumers: #1532/#1533 closeout profile/admission, #1534 docs/skills convergence, and #1515 final milestone closeout.

## Scope Guard

- Do not edit PR body, issue body, or host state from the implementation lane.
- Do not write `.loom/status/current.md`, `.loom/progress/**`, `.loom/reviews/**`, `.loom/shadow/**`, or `.loom/bootstrap/**` from subagents; main thread owns these carriers serially.
- Do not implement queue apply/sync behavior in this PR.
- Do not change hosted admission, failure classifier, or closeout freeze profile semantics.
