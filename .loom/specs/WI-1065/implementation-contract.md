# WI-1065 Implementation Contract

## Write Scope

- `package.json`
- `bin/loom.mjs`
- `test/npm-package-smoke.test.mjs`
- `tools/check_npm_package.py`
- `Makefile`
- `.loom/work-items/WI-1065.md`
- `.loom/progress/WI-1065.md`
- `.loom/reviews/WI-1065.spec.json`
- `.loom/reviews/WI-1065.json`
- `.loom/specs/WI-1065/`
- `.loom/bootstrap/init-result.json`
- `.loom/status/current.md`

## Constraints

- Keep #1065 as the root npm package payload/bin batch.
- Do not add publish workflow, npm token use, tags, GitHub Releases, or npm registry mutation.
- Do not change README hard-cut install guidance here; #1067 owns that.
- Do not broaden to Homebrew, standalone binaries, or repo-specific profile rewrites.
- Do not depend on or package `@mc-and-his-agents/loom-installer`.
