# WI-1961 Implementation Contract

## Scope

- PR metadata contract: `.github/PULL_REQUEST_TEMPLATE.md`, `.loom/companion/repo-interface.json`, and generated template copies.
- Gate/review runtime: `src/skills/shared/scripts/loom_flow.py` and synced runtime copies.
- CLI wrapper/profile routing: `tools/loom.py`.
- Contract fixtures: `tools/check_cli_contract.py`.
- Distribution payload: `plugins/loom/.codex-plugin/plugin.json`.
- Loom carriers: `.loom/work-items/WI-1961.md`, `.loom/progress/WI-1961.md`, `.loom/status/current.md`, `.loom/specs/WI-1961/*`, `.loom/reviews/WI-1961.json`, and related shadow evidence.

## Required Behavior

- PR body machine metadata must not require, render, or compare authored `head_sha`.
- PR head authority must come from GitHub PR readback or explicit CLI override, not from stable PR body metadata.
- PR metadata preflight must continue to require stable Work Item and branch bindings.
- Review disposition must accept validation summary hash/source/locator binding and keep legacy exact summary compatibility.
- `loom ship --validation-profile host-consumer` and `carrier-only` must not schedule Loom source-repository validation commands.
- Generated runtime copies and plugin payload metadata/hash must match source files.
- Existing source-repository validation profiles must continue to run source checks when selected.

## Non-Goals

- No default light-governance host mode.
- No installed-state slimdown.
- No global current pointer/runtime ledger migration.
- No host-only closeout default.
- No batch implementation/closeout engine.
- No host planning taxonomy mapping.
- No existing host slim migration.
- No v0.28.0 release publication.
- No WebEnvoy-specific label hardcoding.
- No downstream repo-local `tools/loom.py` shim requirement.

## Compatibility

- Existing PRs with legacy exact validation summary text remain consumable where the old field is present.
- Explicit `--head-sha` remains a strong CLI override for commands that need a host readback assertion, but it is not authored into the stable machine carrier by default.
- Source-repository profiles keep their current validation behavior.

## Rollback

Revert PR #1970 as a unit if hosted gates show a semantic regression in metadata parsing, review disposition, or validation profile routing. Do not partially restore authored PR body `head_sha` without a new contract decision.
