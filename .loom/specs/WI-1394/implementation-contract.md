# WI-1394 Implementation Contract

- Suite path: minimal

## Contract Surface

- `tools/check_npm_package.py --surface npm-package-manifest` is the named manifest validation surface.
- `tools/check_npm_package.py --surface npm-pack-payload` is the named dry-run package payload validation surface.
- `tools/check_npm_package.py --list-surfaces` exposes the aggregate, manifest, and payload surfaces with commands, evidence labels, evidence locators, and failure labels.
- No-argument `tools/check_npm_package.py` remains the aggregate npm package check and reports both `npm-package-manifest` and `npm-pack-payload` evidence labels.
- Failure output remains fail-closed and reports stable `failed_layer`, `failure_label`, `evidence_label`, `evidence_locators`, and `fallback_to` fields.

## Consumer Boundary

- #1383 evidence labels remain `npm-package-manifest` and `npm-pack-payload`.
- #1393 release-surface work may consume the package labels and commands but this Work Item does not split release validation or redefine release/no-release semantics.
- Release-required downstream work may consume the targeted package surfaces only as package validation evidence, not as proof of release workflow, publish, installed/global CLI, or closeout state.

## Non-Goals

- No release validator split.
- No installed/global CLI smoke.
- No docs/evidence convergence closeout.
- No release cutting, VERSION/tag/GitHub Release/npm publish, or external-visible release action.
- No package payload content change.
- No runtime behavior, skills, demo, or package smoke behavior change beyond validation surface targeting.
- No scheduler-owned review artifact, guardian, formal review, controlled merge, or closeout.

## Validation Binding

- `python3 tools/check_npm_package.py --help`
- `python3 tools/check_npm_package.py --list-surfaces`
- `python3 tools/check_npm_package.py --surface npm-package-manifest`
- `python3 tools/check_npm_package.py --surface npm-pack-payload`
- `python3 tools/check_npm_package.py`
- `make npm-package-manifest-check`
- `make npm-pack-payload-check`
- `make npm-package-check`
- `npm run test:package`
- `python3 tools/loom.py suite inspect --target . --item WI-1394 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1394 --json`
