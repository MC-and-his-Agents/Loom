# WI-1237 Implementation Contract

## Owned Write Surface

- `README.md`
- `docs/methodology/harness/cli-command-matrix.md`
- `docs/methodology/harness/workspace-lifecycle.md`
- `docs/methodology/harness/closeout-gate.md`
- `docs/methodology/harness/host-lifecycle-boundary.md`
- `docs/adoption/loom-cli-release-surface.md`
- `tools/loom.py`
- `tools/check_release_surface.py`
- WI-1237 `.loom/**` carriers, specs, reviews, build evidence, status, and shadows

## Required Behaviors

- Keep `workspace retire` local-only in docs/help; do not imply it closes host objects or writes versioned carriers.
- Keep host closeout sync separate from repo carrier closeout sync.
- Keep `carrier closeout-sync` documented as dry-run by default and host-mutation-free.
- Preserve explicit no-release rationale for docs/help/checker-only work.
- Fail closed in release-doc-contract when the new command names or HotCP-style stale carrier fixture story disappear from required docs.

## Forbidden Scope

- No runtime behavior, schema, parser, failure vocabulary, host mutation, release workflow publish, package payload, VERSION, tag, GitHub Release, npm publish, Round 10/11, Deferred roadmap, #1296, parent #1228, or unrelated refactor changes.
