# WI-1395 Implementation Contract

## Stable Surface

- `tools/check_release_surface.py --surface installed-global-cli-smoke` is the named installed/global CLI smoke validation surface.
- `tools/check_release_surface.py --list-surfaces` exposes the surface name, command, and evidence locator.
- No-argument `tools/check_release_surface.py` remains the aggregate release check and runs the #1393 named release surfaces plus `installed-global-cli-smoke`.

## Smoke Semantics

- The smoke packs the current source checkout into a local npm tarball with `npm pack --pack-destination <tmp> --json --ignore-scripts`.
- The smoke installs that tarball into a temporary npm global prefix with `npm install --global --prefix <tmp>/global <pack.tgz>`.
- The smoke invokes the installed `loom` bin from the temporary prefix and requires `loom version --json` and `loom help --json` to pass.
- The version smoke must report the root `VERSION` value, binding the installed package check to version/package inputs.
- The helper must not mutate the user's real global npm prefix, publish npm, create tags, create releases, or rely on registry state.

## Failure Evidence

- Failures are reported through the existing release-surface failure format with `surface_label=installed-global-cli-smoke`.
- Stable failure labels include package metadata mismatch, npm pack failure, temporary global install failure, missing installed bin, installed command failure, invalid JSON, and version/help contract mismatch.
- The stable evidence locator is `python3 tools/check_release_surface.py --surface installed-global-cli-smoke`.

## Non-Goals

- No package manifest/payload split changes.
- No release/no-release semantic changes.
- No installed runtime behavior changes beyond local smoke validation.
- No #1396 docs/evidence convergence, parent #1260 closeout, umbrella #1255 closeout, or release execution.
