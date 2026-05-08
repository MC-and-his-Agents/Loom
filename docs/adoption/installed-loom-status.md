# Installed Loom Status And Upgrade Rehearsal

Installed Loom surfaces must expose status as evidence, not as a second governance truth source. Repo-owned carriers such as Work Items, PRs, review records, and closeout evidence remain authoritative for project state.

## Installed Surface Status

Installer-managed surfaces write `loom-installed-surface-status/v1` metadata into the installed layer:

- `installed_layer`: `host-adapter-plugin` or `generated-single-skill`
- `host_adapter`: the host adapter that owns discovery, currently `codex` or `claude`
- `mode`: `plugin` or `skill`
- `skill_id`: present for single-skill installs
- `version_context`: repo, installer package, plugin surface, host adapter, skills registry, runtime core, and skill package context when applicable
- `runtime_state`: `ready`, `blocked`, or `unknown`
- `upgrade_eligibility`: `current`, `upgrade-available`, `drift`, `incompatible`, or `unknown`
- `failed_layer` and `fail_closed_reason`: required when the installed surface cannot be trusted

The status distinguishes full host-adapter plugin installs from generated single-skill installs. Unknown, missing, or internally inconsistent version metadata must fail closed with `runtime_state=blocked` and `upgrade_eligibility=incompatible`.

## Upgrade Plan

`loom-installer upgrade-plan plugin|skill <skill-id> --host <host> --target <repo> --json` is a read-only rehearsal command. It reports:

- current installed version context
- available payload version context
- changed paths that would be refreshed by an upgrade
- rollback path for the installed layer
- fail-closed reason when the installed layer cannot be safely interpreted

`upgrade-plan` must not mutate the target repository. It is allowed to report `upgrade-available` when the recorded installed version context is older than the available payload, and `drift` when installed files no longer match their recorded version context.

## Verify Upgrade

`loom-installer verify-upgrade plugin|skill <skill-id> --host <host> --target <repo> --json` is also read-only. It validates the installed layer after rehearsal or install and reports:

- `verified` when installed metadata and payload files match the available payload
- `blocked` when metadata is missing, inconsistent, or payload files drift from the recorded context
- the failed layer and rollback path needed by an operator to keep or restore the last known-good install

These commands are status and rehearsal surfaces only. They must not replace repo companion status, Work Item state, review evidence, or closeout records.
