# Implementation Contract

## Changed Surfaces

- `skills/shared/scripts/runtime_paths.py`
  - Owns workstation root, repo id, global cache root, runtime/tmp locator classification, and physical path mapping.
- `skills/shared/scripts/loom_flow.py`
  - Owns runtime artifact read/write helpers, logical evidence locators, execution attempt read fallback, PR metadata artifact routing, gate freeze artifact routing, review runtime roots, and `.loom/runtime/tmp` scratch routing.
- `tools/loom.py`
  - Owns CLI agent-safe output artifact writes under `.loom/tmp/output-artifacts`.
- Runtime copies
  - `src/skills/shared/scripts/**`, `plugins/loom/skills/shared/scripts/**`, `.loom/bin/**`, and `examples/new-project/.loom/bin/**` mirror the shared runtime changes.
- `tools/check_cli_contract.py`
  - Owns focused regression coverage and fixture expectations.

## Invariants

- `.loom/runtime/**` logical locators map to `~/.loom/repos/<repo-id>/runtime/**` for writes.
- `.loom/tmp/**` logical locators map to `~/.loom/repos/<repo-id>/tmp/**` for writes.
- Repo truth carriers remain repo-local.
- Payloads continue to expose logical locators, not workstation-specific absolute paths.
- Legacy repo-local runtime evidence may be read as fallback only when global cache evidence is absent.

## Non-Goals

- Do not implement #1900 repo carrier summary slimming.
- Do not implement #1901 full gate independence audit.
- Do not implement #1908 legacy migration commands.
- Do not change CLI marketplace, npm install, or host plugin upgrade behavior.

## Risk Controls

- Keep helper behavior small and path-prefix based.
- Reuse the workstation repo id algorithm already used by registry code.
- Validate both direct helper behavior and real consumer behavior.
- Sync generated/runtime payload copies in the same PR.
