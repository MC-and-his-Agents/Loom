# WI-1296 Implementation Contract

## Owned Write Surface

- `VERSION`
- `package.json`
- `skills/loom-*/loom-package.json`
- WI-1296 `.loom/**` carriers, specs, reviews, build evidence, status, and shadows

## Required Behaviors

- Use v0.14.1 as the release target only after tag, GitHub Release, and npm preflight prove it is unoccupied.
- Keep `VERSION`, root npm package version, and generated skill `repo_version` surfaces synchronized.
- Use the existing `loom-cli-release` workflow for publication after main merge; do not publish locally.
- Bind final release evidence to the main merge commit and read back tag, GitHub Release, npm package, and installed/global CLI smoke before closing #1296.
- Preserve parent #1228 and Round 9 milestone closeout until #1296 is CLOSED/COMPLETED.

## Forbidden Scope

- No release workflow semantic changes.
- No npm package payload policy changes beyond the version surfaces.
- No local manual npm publish, manual git tag, or manual GitHub Release creation.
- No installer legacy release line changes.
- No runtime behavior, schema, parser, failure vocabulary, security/privacy, Round 10/11, Deferred roadmap, parent #1228 closeout before #1296 completion, or unrelated refactors.
