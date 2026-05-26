# WI-1066 Implementation Contract

## Write Scope

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1066.md`
- `.loom/progress/WI-1066.md`
- `.loom/reviews/WI-1066.spec.json`
- `.loom/reviews/WI-1066.json`
- `.loom/specs/WI-1066/`
- `.loom/bootstrap/init-result.json`
- `.loom/status/current.md`

## Constraints

- Keep #1066 focused on CLI-managed plugin/SKILLS install and verification.
- Do not add npm publish automation, npm token usage, tags, GitHub Releases, or registry mutation.
- Do not hard-cut README or primary install docs here; #1067 owns that.
- Do not add Homebrew, standalone binaries, or repo-specific profile rewrites.
- Do not invoke or depend on `@mc-and-his-agents/loom-installer` or `packages/loom-installer/dist` for plugin/SKILLS installation.
