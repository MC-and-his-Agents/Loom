# WI-1507 Plan

## Implementation Steps

1. Add `docs/methodology/harness/gate-freeze.md` as the authoritative `loom-gate-freeze/v1` contract.
2. Define the snapshot envelope, required subject fields, input binding fields, vocabulary versions, readiness output, failure classifier, release evidence boundary, and positive/negative examples.
3. Update harness README and CLI command matrix to reference the planned gate freeze surface without declaring implemented commands.
4. Record WI-1507 Work Item, progress, spec, plan, implementation contract, evidence map, and task carrier.
5. Run focused local validation and prepare PR metadata/readback for #1507.

## Validation

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py help --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1507 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1507 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1507 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 .loom/bin/loom_init.py fact-chain --target .`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py build --target . --item WI-1507 --build-evidence .loom/runtime/build/WI-1507.json --json`
- PR metadata preflight/readback and hosted checks before merge.

## Dependencies

- Parent FR: #1505.
- Hard dependency: none.
- Read-only references: #873, #874, #877, #932, #370, #320, #957, #1285.

## Scope Guard

- Do not implement #1508 or later milestone/12 issues in this PR.
- Do not modify `.github/workflows`, PR templates, generated skills payload, runtime parser behavior, release workflows, package metadata, VERSION, tags, GitHub Releases, npm state, or external host settings.
