# WI-1892 Implementation Contract

## Scope

- User installation and upgrade guidance: `README.md`.
- Global CLI/user plugin boundary: `docs/adoption/global-cli-user-plugin-contract.md`.
- Host adapter boundary: `docs/adoption/host-adapter-matrix.md`.
- Loom carriers: `.loom/work-items/WI-1892.md`, `.loom/progress/WI-1892.md`, `.loom/status/current.md`, `.loom/specs/WI-1892/*`, and `.loom/reviews/WI-1892*.json`.

## Required Behavior

- README must explain that the Loom source marketplace can install or update only the Codex plugin surface.
- README must explain that global CLI installation and upgrade remain npm-owned.
- README must explain that each target repository still needs its own Loom adoption or runtime-upgrade validation.
- The global CLI/user plugin contract must classify Codex marketplace plugin update as workstation truth, not repository adoption truth.
- The Codex host adapter matrix must list npm CLI, user-level plugin install/register or marketplace update, and per-repository validation as separate surfaces.
- Validation must prove the documentation changed without modifying CLI/runtime/plugin payload behavior.

## Non-Goals

- Do not change CLI commands, runtime behavior, package distribution, plugin manifest, marketplace catalog, or skill payload.
- Do not implement workstation registry, global cache, upgrade orchestration, legacy migration, or multi-repository mutation.
- Do not mutate a real user Codex profile or marketplace configuration.
