# WI-859 Plan

## Steps

- Add profile parsing and auto-detection to `loom_check.py`.
- Split source/distribution checks from consumer runtime/adoption checks.
- Validate consumer carriers, manifest runtime hashes, consumer command chain, and merge-ready/checkpoint result shape.
- Update consumer-facing generated README and harness docs.
- Regenerate skills and demo runtime surfaces.
- Stabilize source self-check fixtures exposed by CI and default auto profile.
- Bump installer version metadata for changed runtime payload behavior.
- Bind PR #960 to `WI-859`, record fresh review evidence, and drive merge-ready, merge, and closeout consistency.

## Validation

- `git diff --check`
- `python3 tools/py_compile_clean.py tools/loom_init.py tools/loom_flow.py tools/loom_check.py tools/loom_status.py skills/shared/scripts/*.py src/skills/shared/scripts/*.py`
- `python3 tools/skills_surface.py check`
- `node packages/loom-installer/scripts/check-version-bump.mjs --base origin/main`
- `make loom-demo-new-project`
- `python3 tools/loom_check.py --profile source .`
- `python3 tools/loom_check.py .`
- `make check`
- Syvert read-only consumer smoke using this branch runtime

## Closeout

After PR #960 merges, confirm main contains the merge commit, #859/#860/#861 are closed by the PR body or closeout sync, and `WI-859` progress reflects the merged/retired state.
