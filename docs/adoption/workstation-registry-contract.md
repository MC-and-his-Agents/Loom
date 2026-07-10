# Workstation Registry Contract

`~/.loom/repositories.json` is workstation truth for discovering Loom-enabled
repositories on one machine. It speeds batch planning, diagnostics, recovery,
and upgrades by avoiding repeated repository discovery. It is not repository
truth, governance truth, or closeout evidence.

This contract freezes the schema for #1894. #1895 may add CLI read/write
commands, and #1896 may add fail-closed validation behavior, but neither should
change the authority boundary without updating this document and its fixtures.

## Authority

The registry is owned by the workstation:

- canonical path: `~/.loom/repositories.json`
- schema version: `loom-workstation-repositories/v1`
- authority: `workstation`
- mutation owner: `loom workstation register|unregister`
- read owner: `loom workstation list`, `loom workstation upgrade --plan`

The registry may cache facts that are useful on this machine:

- repository path
- repository id
- remote URL hash
- adoption mode
- last seen Loom version
- opt-in state
- last seen timestamp

The registry must not cache or replace repository-owned truth:

- no Work Item status
- no issue/PR/review/closeout authority
- no merge-ready decision
- no long runtime logs
- no plugin payload or CLI runtime payload
- no repository mutation proof

## Schema

Minimal valid shape:

```json
{
  "schema_version": "loom-workstation-repositories/v1",
  "authority": "workstation",
  "registry_path": "~/.loom/repositories.json",
  "updated_at": "2026-07-02T00:00:00Z",
  "repositories": [
    {
      "id": "repo_6f1b7a2c9d4e",
      "path": "/Users/example/dev/TargetRepo",
      "path_state": "present",
      "remote": {
        "canonical_url": "git@github.com:owner/TargetRepo.git",
        "hash": "sha256:3eb0f0a1e8d2f2f0e64d1f4a0d8d8f4df6f4e2f2d3c2b1a09f8e7d6c5b4a3210",
        "observed_at": "2026-07-02T00:00:00Z"
      },
      "adoption": {
        "mode": "metadata-only",
        "installed_state_schema": "loom-installed-state/v2",
        "last_seen_version": "v0.26.0"
      },
      "opt_in": {
        "enabled": true,
        "source": "loom workstation register",
        "updated_at": "2026-07-02T00:00:00Z"
      },
      "last_seen_at": "2026-07-02T00:00:00Z"
    }
  ]
}
```

## Field Rules

Top-level fields:

| Field | Rule |
| --- | --- |
| `schema_version` | Must equal `loom-workstation-repositories/v1`. |
| `authority` | Must equal `workstation`. |
| `registry_path` | Must identify `~/.loom/repositories.json`; host-expanded absolute paths are allowed in CLI output, but fixtures use the logical path. |
| `updated_at` | ISO-8601 UTC timestamp for the registry write. |
| `repositories` | Array of repository entries; ids must be unique. |

Repository entry fields:

| Field | Rule |
| --- | --- |
| `id` | Stable workstation-local id. It must not be reused for a different path or remote hash. |
| `path` | Absolute local repository path. Relative paths fail closed. |
| `path_state` | `present`, `missing`, or `unknown`. Only `present` is eligible for mutation planning. |
| `remote.canonical_url` | Canonical git remote URL observed during registration. Empty only when the repository has no remote and `remote.state = "missing"`. |
| `remote.hash` | `sha256:<hex>` of the canonical remote URL, or `null` when `remote.state = "missing"`. |
| `remote.observed_at` | Timestamp for the remote read. |
| `adoption.mode` | `metadata-only`, `repo-local-wrapper`, `legacy-embedded`, or `unknown`. |
| `adoption.installed_state_schema` | Installed-state schema last read from the repository, or `null` when unknown. |
| `adoption.last_seen_version` | Loom version last observed in the repository metadata, or `null` when unknown. |
| `opt_in.enabled` | `true` means workstation upgrade planning may include the repo. `false` means list-only unless explicitly re-registered. |
| `opt_in.source` | Operator or command source for the opt-in state. |
| `opt_in.updated_at` | Timestamp for the opt-in decision. |
| `last_seen_at` | Timestamp for the last successful repository read. |

## Fail-Closed Classification

The registry is an accelerator, not authority. Any ambiguity blocks mutation
planning for that entry and falls back to per-repository verification:

| Classification | Condition | Behavior |
| --- | --- | --- |
| `path_missing` | `path_state != "present"` or the local path no longer exists. | Do not mutate; ask for unregister or path repair. |
| `remote_hash_drift` | Current canonical remote hash differs from `remote.hash`. | Do not mutate; require explicit re-register. |
| `repo_id_conflict` | The same `id` appears for multiple path/remote pairs. | Do not mutate either entry; require manual repair. |
| `opted_out` | `opt_in.enabled = false`. | Exclude from upgrade apply; show in list/plan diagnostics. |
| `schema_unsupported` | Unknown schema version or missing required fields. | Ignore for mutation planning; recommend registry repair. |

These classifications are fixture-covered in
`docs/evidence/fixtures/workstation-registry-fixtures.json`.

## Consumer Boundary

`loom workstation upgrade --plan` may use the registry to avoid rediscovering
repositories, but each candidate repository still needs its own adoption
validation before repo mutation. A registry entry can say "this machine saw a
repo here"; it cannot say "that repo is merge-ready", "that issue is done", or
"that repository has successfully upgraded".

The plan output is read-only and classifies work at two levels:

| Classification | Meaning |
| --- | --- |
| `machine_only` | Machine-level CLI/plugin refresh and host doctor steps; no repository mutation. |
| `repo_noop` | Repository is opted out or already appears current for the requested target version. |
| `repo_auto_commit_candidate` | Metadata-only adoption can be refreshed with low-risk repo-local metadata changes. |
| `repo_pr_required` | Legacy or repo-local-wrapper adoption may rewrite tracked surfaces and needs a repo-scoped PR. |
| `blocked` | Registry identity/path drift or unknown adoption state blocks planning until repaired. |

## CLI Surface

The #1895 command slice implements the minimum registry read/write surface:

```bash
loom workstation register --target <repo> --json
loom workstation list --json
loom workstation upgrade --plan --to <version> --json
loom workstation upgrade --apply --to <version> --json
loom workstation upgrade --apply --to <version> --target <repo> --json
loom workstation current --target <repo> --json
loom workstation current --target <repo> --item <WI> --issue <issue> --pr <pr> --branch <branch> --apply --json
loom workstation current --target <repo> --clear --apply --json
loom workstation unregister --target <repo> --json
loom workstation unregister --id <repo-id> --json
loom workstation unregister --target <repo> --keep-entry --json
```

`register` writes only `~/.loom/repositories.json`. It reads the target path,
`git remote.origin.url`, and any available `.loom/installed-state.json`
metadata to populate one workstation registry entry. It must not write runtime,
plugin, skills, adoption, issue, PR, review, or closeout payload into the target
repository.

`list` is read-only. It may report stored-entry diagnostics such as `opted_out`
or malformed stored entries, but it does not replace repository-local adoption
validation.

`upgrade --plan` is read-only. Its machine plan must include the npm CLI
upgrade command, Codex user plugin refresh guidance, and a host doctor readback.
When the workstation uses a Codex marketplace source for Loom, the plugin
refresh guidance may point at that marketplace update path; otherwise it falls
back to `loom host install|register --host codex --scope user`.

`upgrade --apply` performs the machine-level refresh only unless `--target
<repo>` is supplied. Repository mutation is deliberately single-repository and
explicit in the first version: only a registered `repo_auto_commit_candidate`
may be refreshed directly. `repo_pr_required`, `blocked`, unknown, or ambiguous
entries must remain PR/manual flows.

Within one `workstation upgrade` invocation, host/plugin freshness readback is a
single-invocation cache. It may be reused across repository classifications, but
it must be invalidated when the target version, source package version, Codex
plugin payload hash, Codex marketplace/runtime cache, or host doctor result
changes.

`current` reads or writes `~/.loom/repos/<repo-id>/current.json`. A read is
non-mutating. Applying `--item ...` marks the local workstation's active item;
applying `--clear` records `no_active_item`. This surface is only a local
execution pointer and must not mutate `.loom/status/current.md` or any
repository carrier.

`unregister` removes the matching entry by target path or id. With
`--keep-entry`, it leaves the entry visible for diagnostics and sets
`opt_in.enabled = false`, making the entry list-only for later upgrade planning.
