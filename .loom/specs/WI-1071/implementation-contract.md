# WI-1071 Implementation Contract

## Owned Surfaces

- `src/skills/shared/scripts/loom_flow.py`
- `src/skills/shared/scripts/loom_check.py`
- `skills/shared/scripts/loom_flow.py`
- `skills/shared/scripts/loom_check.py`
- `.loom/bin/loom_flow.py`
- `.loom/bin/loom_check.py`
- `skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py`
- `skills/loom-*/.loom-runtime/shared/scripts/loom_check.py`
- `docs/methodology/harness/*.md` for controlled merge, PR merge gate, host action, and failure taxonomy boundaries
- matching shared reference copies under `src/skills/shared/references`, `skills/shared/references`, and generated skill runtime references

## Invariants

- `HOST_MERGEABILITY_HARD_BLOCK_STATUSES` contains `DIRTY` and `DRAFT`.
- `BLOCKED` is not appended to missing controlled merge inputs by itself.
- The drift readback exposes the `delegated_host_policy` interpretation for `BLOCKED`.
- Authored approval truth remains sourced from the Loom review record, not GitHub review/comment state.
- The merge operation remains host-delegated through `gh pr merge`.

## Validation

- `python3 tools/py_compile_clean.py ...`
- `python3 tools/skills_surface.py check`
- `git diff --check`
- runtime/reference parity check
- `python3 tools/loom_check.py --profile source --source-surface source-self-fixture .`
- `python3 tools/loom_check.py --profile source --source-surface contract-only .`
