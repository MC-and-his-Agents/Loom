# WI-1064 Implementation Contract

## Write Scope

- `docs/adoption/cli-only-install-contract.md`
- `docs/adoption/README.md`
- `docs/adoption/loom-cli-release-surface.md`
- `docs/adoption/version-authority-map.md`
- `.loom/work-items/WI-1064.md`
- `.loom/progress/WI-1064.md`
- `.loom/reviews/WI-1064.spec.json`
- `.loom/reviews/WI-1064.json`
- `.loom/specs/WI-1064/`
- `.loom/bootstrap/init-result.json`
- `.loom/status/current.md`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Constraints

- Keep #1064 as a contract-freeze batch.
- Do not change package manifests, publish workflows, npm registry state, tags, or GitHub Releases.
- Do not remove existing README install commands here; #1067 owns the hard cut.
- Do not broaden to Homebrew, standalone binaries, or repo-specific profile rewrites.
