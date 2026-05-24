# WI-906 Spec

## Behavior Contract

WI-906 implements the #888 installed surface detection layer while consuming the #887 installed-state contract.

Observable behavior:

- `python3 tools/loom.py detect --target <repo> --json` emits `loom-cli-output/v1` with `schema: loom-installed-surface-detect/v1`, a classification, and a surface list.
- `python3 tools/loom.py doctor --target <repo> --json` emits `schema: loom-installed-surface-doctor/v1` and passes only when installed-state v2 validates and no blocking legacy surface remains.
- `python3 tools/loom.py repair plan --target <repo> --json` emits `schema: loom-installed-surface-repair-plan/v1` and never mutates the target.
- `python3 tools/loom.py repair apply --target <repo> --json` fails closed with the generated plan until a later Work Item approves write ownership and rollback semantics.
- Legacy `.loom/bin`, `.agents/skills`, generated skills registries, plugin manifests, old installer status, single-skill packages, and symlinked surfaces are diagnostic evidence only. They do not satisfy installed-state validation.

## Boundaries

- #888 does not implement installer shim behavior from #893.
- #888 does not implement host adapter orchestration from #894.
- #888 does not generate, sync, package, or release-check skills for #895.
- WebEnvoy/Syvert/HotCP coverage is synthetic legacy surface validation, not repository-specific rule import.

## Acceptance

- `tools/check_cli_contract.py` mechanically covers empty, legacy, mixed legacy, valid, invalid, and graph-edge negative cases.
- Blocking outputs include `failed_layer`, `fail_closed_reason`, and executable `fallback_to`.
- `repair plan` includes ordered actions and `mutates: false`.
- `repair apply` remains a structured block rather than modifying files.
