# WI-1486 Implementation Contract

## Scope

- Update Codex user-level plugin skill payload text so executable skills call the global `loom` CLI and consume agent-safe summary / artifact locator output by default.
- Synchronize `src/skills`, generated `skills`, and `plugins/loom/skills`.
- Add minimal Loom carriers for WI-1486 review and closeout consumption.

## Contract

- Scenario skill command examples use global `loom ... --json`.
- Full diagnostics require explicit `--full-output` or artifact locator reads for debugging, audit, or blocker classification.
- Handoff and thread rotation packages pass summary and authoritative locators, not complete logs, full command JSON, or old full thread turns.
- Artifact locators are diagnostic evidence, not authored truth carriers.
- The plugin payload does not vendor runtime and does not restore repo-local plugin/runtime/skills, single-skill package, or old installer paths.

## Non-Goals

- Do not update README, ordinary CLI help text, adoption migration docs, release notes, package metadata, or downstream repositories.
- Do not change runtime output envelope implementation or budget behavior.

## Validation

- `python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity`
- targeted stale command/string `rg`
- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py`
- `python3 tools/loom.py suite validate --target . --item WI-1486 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json`
- `python3 tools/loom.py fact-chain --target . --json`
- `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
- `git diff --check`
