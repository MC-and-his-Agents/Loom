# WI-1891 Implementation Contract

## Scope

- Published catalog: `.agents/plugins/marketplace.json`.
- Marketplace target plugin manifest: `plugins/loom/.codex-plugin/plugin.json`.
- Source self-plugin Makefile gate: `Makefile` target `loom-self-plugin-check`.
- Loom carriers: `.loom/work-items/WI-1891.md`, `.loom/progress/WI-1891.md`, `.loom/status/current.md`, `.loom/specs/WI-1891/*`, and `.loom/reviews/WI-1891*.json`.
- Predecessor carrier sync: `.loom/progress/WI-1890.md` terminal checkpoint alignment only.

## Required Behavior

- The source repository must publish a Codex marketplace catalog named `loom`.
- The catalog must expose exactly one plugin entry named `loom`.
- The plugin entry must use local source path `./plugins/loom`.
- The plugin entry must use `policy.installation: AVAILABLE`, `policy.authentication: ON_INSTALL`, and `category: Productivity`.
- Codex must parse the repository root as a marketplace when run with a temporary `HOME`.
- The source self-plugin Makefile check must validate the expected published catalog file instead of forbidding it.
- The predecessor WI-1890 carrier must be terminal so WI-1891 purity/state checks do not see two active items.

## Non-Goals

- Do not mutate the user's real Codex profile or marketplace configuration.
- Do not implement CLI/plugin automatic upgrades, workstation registry, global runtime cache, repo adoption refresh, or legacy migration.
- Do not change the packaged Loom plugin payload, skills, or runtime copies.
- Do not document the broader install-boundary guidance; #1892 owns that slice.
