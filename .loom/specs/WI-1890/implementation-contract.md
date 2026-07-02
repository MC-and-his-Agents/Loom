# WI-1890 Implementation Contract

## Scope

- Checker source: `src/skills/shared/scripts/loom_check.py`.
- Generated checker copies: `skills/shared/scripts/loom_check.py`, `plugins/loom/skills/shared/scripts/loom_check.py`, `.loom/bin/loom_check.py`, and demo bootstrap runtime fixture.
- Adoption contract docs: `docs/adoption/installation-taxonomy.md`, `docs/adoption/global-cli-user-plugin-contract.md`, `docs/evidence/README.md`.
- Plugin payload metadata: `plugins/loom/.codex-plugin/plugin.json`.
- Loom carriers: `.loom/work-items/WI-1890.md`, `.loom/progress/WI-1890.md`, `.loom/status/current.md`, `.loom/specs/WI-1890/*`, and `.loom/reviews/WI-1890*.json`.

## Required Behavior

- The source checker must accept only a deterministic published Loom Codex marketplace catalog shape for the Loom source repository.
- The accepted catalog shape must expose exactly the `loom` plugin, point to local `./plugins/loom`, and mark installation as `AVAILABLE`.
- The checker must continue to reject workstation installed-state or cache-like keys such as `enabled`, `installed`, `installed_at`, `cache`, `cache_path`, and `runtime_cache`.
- The checker must reject marketplace entries that point outside `./plugins/loom`.
- Adoption docs must state that a published marketplace catalog is distribution metadata, not user/workstation installed state.
- Generated runtime, skills, demo fixture, and plugin payload metadata must stay synchronized.

## Non-Goals

- Do not add `.agents/plugins/marketplace.json`; #1891 owns the actual catalog file.
- Do not implement Codex marketplace installation or automatic plugin upgrade behavior.
- Do not implement global workstation registry, global runtime cache, workstation upgrade orchestration, or legacy migration.
- Do not allow downstream repositories to record Codex plugin installed-state truth in `.agents/plugins/marketplace.json`.
