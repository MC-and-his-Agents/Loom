# WI-1541 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/loom.py pr metadata-render` delegates to runtime `pr-metadata render`.
- `tools/loom.py pr metadata-readback` delegates to runtime `pr-metadata readback`.
- `tools/loom.py pr metadata-update` delegates to runtime `pr-metadata update`.
- Runtime render writes a repo-relative body artifact and validates it with metadata preflight.
- Runtime readback parses artifact or host PR body and exposes legacy bindings plus governance fields.
- Runtime update renders, applies `gh pr edit --body-file`, reads the host body back, and validates the rendered/readback pair.
- `closeout` requests reuse the existing `merge_ready` carrier surface rather than creating a duplicate machine schema.
- Focused `pr-metadata` contract checks cover wrapper delegation, render/readback behavior, closeout surface reuse, and generated runtime parity.

## Consumer Boundary

- #1514/#1534 may document `loom pr metadata-update` as the preferred PR body machine carrier update path.
- #1512/#1533/#1515 may use this surface to reduce manual PR body drift, but this PR does not change their admission or closeout semantics.

## Non-Goals

- Do not implement hosted admission, closeout-specific gate behavior, one-shot post-merge closeout, Work Item startup audit UX, or release/no-release closeout.
- Do not replace GitHub or `gh`; the update surface wraps the existing host operation and requires readback.

## Validation Binding

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py pr --help`
- `git diff --check`
