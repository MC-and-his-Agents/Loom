# WI-1396 Implementation Contract

- Work Item: WI-1396
- Issue: #1396
- Branch: work/1396-release-package-docs-evidence

## Contract Surface

- Release validation named surfaces remain:
  - `release-doc-contract`
  - `release-workflow-contract`
  - `installer-sunset-guard`
  - `forbidden-release-surface-patterns`
  - `installed-global-cli-smoke`
- Release aggregate validation remains available through `python3 tools/check_release_surface.py` and explicit `--surface aggregate-release-surface`.
- Npm package validation named surfaces remain:
  - `npm-package-manifest`
  - `npm-pack-payload`
- Npm package aggregate validation remains available through `python3 tools/check_npm_package.py` and explicit `--surface aggregate`.
- `npm run test:package` remains package payload smoke evidence when package payload proof is required.

## Consumer Boundary

- This Work Item updates docs/evidence references only.
- Release-required downstream work may consume named surfaces or aggregate surfaces when retained evidence includes label, command, head or merge commit, run/transcript locator, result, and consumer boundary.
- This Work Item does not close #1260 or #1255 and does not replace release/no-release closeout evidence for any downstream Work Item.

## Non-Goals

- No checker behavior changes.
- No Makefile changes unless a locator bug blocks #1396.
- No release/no-release semantic change.
- No release execution, VERSION/tag/GitHub Release/npm publish, workflow behavior, package payload, runtime behavior, or external-visible action.
- No `.loom/reviews/**`, `.loom/status/current.md`, `.loom/shadow/**`, parent #1260 closeout, umbrella #1255 closeout, guardian/formal review, or controlled merge.

## Validation Binding

- `python3 tools/check_release_surface.py --list-surfaces`
- `python3 tools/check_release_surface.py --surface aggregate-release-surface --show-surface-evidence`
- `python3 tools/check_npm_package.py --list-surfaces`
- `python3 tools/check_npm_package.py`
- `npm run test:package`
- `python3 tools/loom.py suite inspect --target . --item WI-1396 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1396 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1396 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1396 --json`
