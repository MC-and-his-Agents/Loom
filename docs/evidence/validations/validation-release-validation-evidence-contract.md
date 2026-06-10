# Validation: Release Validation Evidence Contract

This record is the WI-1383 contract evidence for the minimal release validation and release closeout evidence labels consumed by #1260 and downstream release-required work (#1296, #1246, #1293).

## Contract Scope

WI-1383 freezes evidence semantics only. It does not implement the full release/npm checker split, cut a release, change workflow behavior, change package/version files, or change user-visible CLI/runtime behavior.

Frozen evidence labels:

- `release-doc-contract`
- `release-workflow-contract`
- `installer-sunset-guard`
- `forbidden-release-surface-patterns`
- `npm-package-manifest`
- `npm-pack-payload`
- `installed-global-cli-smoke`

The current compatible aggregate commands remain:

- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `npm run test:package` when practical and when it consumes the npm package contract

Downstream release-required Work Items may cite these labels for release evidence semantics without waiting for #1260 to split the scripts. They must still record their own release/no-release closeout evidence on their own current heads and merge commits.

## No-Release Basis For WI-1383

WI-1383 is `no_release`: it changes release evidence documentation and Loom carriers only. It does not change `VERSION`, `package.json`, generated skills package versions, release workflows, npm publish behavior, root package payload semantics, runtime code, CLI behavior, tags, GitHub Releases, or npm registry state.

## Validation Record

Local validation for the WI-1383 docs-only contract surface:

- `git diff --check`: pass.
- Focused readback for `release-doc-contract`, `release-workflow-contract`, `installer-sunset-guard`, `forbidden-release-surface-patterns`, `npm-package-manifest`, `npm-pack-payload`, `installed-global-cli-smoke`, release-required closeout fields, and `no_release` rationale: pass.
- `python3 tools/check_release_surface.py`: pass.
- `python3 tools/check_npm_package.py`: pass.
- `npm run test:package`: pass.
- `python3 tools/loom.py suite inspect --target . --item WI-1383 --json`: pass, with path decision `.loom/specs/WI-1383/spec.md`.
- `python3 tools/loom.py suite validate --target . --item WI-1383 --json`: expected `result=not_applicable`, `blocking_gaps=[]`, and no findings for docs-only scope.
- `python3 .loom/bin/loom_init.py fact-chain --target .`: pass for the unchanged repo bootstrap current item, which remains `WI-1254`.
- `python3 .loom/bin/loom_init.py verify --target .`: pass for the unchanged repo bootstrap current item, which remains `WI-1254`.

Carrier boundary: WI-1383 is issue-scoped in `.loom/progress/WI-1383.md` and `.loom/specs/WI-1383/spec.md`. The global `.loom/bootstrap/init-result.json` and `.loom/work-items/**` carriers still point to WI-1254 and are outside the WI-1383 worker write scope. This record does not claim a global fact-chain switch to WI-1383.
