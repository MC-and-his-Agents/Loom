# WI-1578 Implementation Contract

- Suite path: minimal

## Contract Surface

- `loom pr metadata-render --surface closeout` emits a PR metadata machine carrier with `surface: closeout`.
- `loom pr metadata-preflight --surface closeout` consumes a closeout machine carrier as closeout metadata.
- `loom pr metadata-readback --surface closeout` reports `machine_surface: closeout` for closeout PR bodies.
- Review and pre-review metadata compatibility with declared `merge_ready` carriers remains unchanged.
- Generated skill runtime copies stay in parity with `src/skills/shared/scripts/loom_flow.py`.
- Focused `tools/check_cli_contract.py --surface pr-metadata` covers render, preflight, and compatibility behavior.

## Consumer Boundary

- PR #1577 closeout-only carrier sync, PR gate, hosted checks, and milestone/12 closeout may consume this contract only as the PR metadata closeout surface fix.
- #1533/#1534/#1515 may consume the stable surface name after #1578 is merged and #1577 metadata has been regenerated/read back.

## Non-Goals

- Do not modify #1577 closeout-only carrier files.
- Do not change hosted admission, controlled merge, release/no-release judgment, closeout gate semantics, or one-shot post-merge closeout run behavior.
- Do not add or rename PR metadata schema fields beyond the effective surface value.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1578 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1578 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1578 --json`
- `git diff --check`
