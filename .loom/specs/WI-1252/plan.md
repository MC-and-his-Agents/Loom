# WI-1252 Plan

## Implementation Steps

- Reuse prepared source fixture baselines for daily execution CLI review-run and installed-runtime setup where safe.
- Keep every target fixture copy isolated through fresh clone/copy targets and private host discovery environment.
- Synchronize the shared `loom_check.py` runtime copies and demo bootstrap hashes.
- Preserve adjacent Round 7 ownership boundaries for #1249, #1250, #1251, and #1253.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py` for synchronized `loom_check.py` copies
- `python3 tools/skills_surface.py check`
- `make loom-demo-new-project-check`
- `make repo-local-cli-fast GROUP=setup-demo-bootstrap`
- `PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface review-run .`
- `PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 tools/loom_check.py --source-surface installed-runtime .`
- PR metadata preflight/readback and hosted check readback on the current PR head

## Ownership Constraints

- WI-1252 owns only snapshot/bootstrap cost reduction, hostless fixture isolation, synchronized runtime/demo parity, branch-local WI-1252 carriers, and validation evidence.
- WI-1252 does not rename #1249 progress/timing/failure labels.
- WI-1252 does not split or rename #1250 review-run fixture groups.
- WI-1252 does not change #1251 fallback truth boundaries.
- WI-1252 does not define #1253 fast/full entrypoint policy.
