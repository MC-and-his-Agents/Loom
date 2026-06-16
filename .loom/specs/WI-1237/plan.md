# WI-1237 Plan

## Implementation Steps

1. Update README with idle closeout recovery steps and the three lifecycle layers.
2. Update harness docs for CLI command matrix, workspace lifecycle, closeout gate, and host lifecycle boundary.
3. Update root CLI help summaries so `help --json` names local retire, host closeout sync, and carrier closeout sync boundaries.
4. Update release-surface docs and `tools/check_release_surface.py` so release-doc-contract validation covers the new command names and HotCP-style stale carrier fixture story.
5. Record WI-1237 carriers, evidence map, and validation summaries for review/merge-ready consumption.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py help --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py --surface release-doc-contract`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py skills release-check --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1237 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1237 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1237 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --json`
- PR metadata preflight/readback, hosted checks, pr-gate, controlled merge, and post-merge closeout readback before closing #1237.

## Dependencies

- Hard dependency consumed: #1235 stable repair/sync behavior merged through closeout PR #1506 at merge commit `703feadf46162d7937ede040a098a013093b2c39`.
- Hard dependency consumed: #1236 HotCP-style stale active fixture and closeout sync merged through PR #1517 at merge commit `47083d932490b76a49f97d9a0cb307134582282b`.
- Convergence dependency: #1296 release/no-release closeout starts only after #1237 merges.

## Scope Guard

- Do not touch #1296 release/no-release closeout, parent #1228 closeout, Round 10/11, Deferred roadmap, VERSION/tag/GitHub Release/npm publish, release workflow publish behavior, package payload behavior, runtime behavior, shared schema/parser/failure vocabulary, or unrelated refactors.
