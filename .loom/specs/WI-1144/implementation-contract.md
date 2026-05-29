# Implementation Contract

## Owned Change Surface

- `package.json`
- `tools/check_npm_package.py`
- `tools/loom.py`
- `tools/check_cli_contract.py`
- `test/npm-package-smoke.test.mjs`
- `.loom/work-items/WI-1144.md`
- `.loom/progress/WI-1144.md`
- `.loom/specs/WI-1144/*`

## Contract

- Root `loom` npm package payload must include suite source-truth docs used by suite automation consumers.
- `tools/check_npm_package.py` must fail closed when those docs are absent from manifest or `npm pack --dry-run` output.
- `loom skills release-check --json` must consume package dry-run validation before reporting pass.
- CLI output remains evidence only and must not replace Work Item, review, merge-ready, closeout, Project, or docs/source truth.
