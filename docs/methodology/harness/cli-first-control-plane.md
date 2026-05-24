# CLI-First Control Plane

Loom's CLI owns executable operating semantics. Skills, plugins, installer shims, and repo-local carriers may expose entry points, but they do not own the truth of command behavior.

## Authority Split

| Surface | Responsibility | Must not own |
| --- | --- | --- |
| `loom` CLI | Command semantics, JSON output, fail-closed behavior, install-state interpretation, and execution orchestration. | Business backlog truth or host-owned GitHub state. |
| `SKILLS` | Agent-facing scenario entry and host discovery text. They call CLI commands or consume CLI JSON. | Core algorithms, upgrade truth, or hidden state transitions. |
| Plugins / host adapters | Native host discovery, tool mapping, bootstrap wiring, and adapter version metadata. | Installation graph truth or governance truth. |
| `.loom/` | Repo execution facts: companion contracts, work items, review evidence, status, checkpoints, and installed-state metadata when adopted. | Global Loom distribution truth or external backlog truth. |
| `loom-installer` | Legacy compatibility shim and adapter-managed install path. | Primary command semantics after CLI-first adoption. |

## Command Contract

Every top-level `loom` command is one of:

- `implemented`: executable in the current CLI.
- `delegated`: compatibility route to an existing repo-local wrapper.
- `reserved`: frozen in the command matrix but intentionally fail-closed until its Work Item implements it.

Reserved commands must return structured JSON with:

- `schema_version: loom-cli-output/v1`
- `result: block`
- `failed_layer`
- `fail_closed_reason`
- `fallback_to`

They must not silently call an unrelated legacy wrapper. This keeps future command names stable without pretending that later phase work is complete.

## JSON Output

Machine-readable CLI commands use `loom-cli-output/v1` unless a narrower command contract states otherwise. The minimum fields are:

- `schema_version`
- `command`
- `result`: `pass` or `block`
- `generated_at`
- `summary`

Blocking outputs add `failed_layer`, `fail_closed_reason`, and `fallback_to`. Commands that inspect target repository state also include `target`.

## Fail-Closed Rules

The CLI must fail closed when:

- the command is unknown;
- a reserved command is invoked before implementation;
- a delegated wrapper is missing;
- target installed-state metadata is missing, unreadable, or not `loom-installed-state/v2`;
- installed layers have missing, unknown, or inconsistent version metadata;
- a non-ready layer omits `failed_layer` or `fail_closed_reason`.
- installed surface diagnostics find only legacy, mixed, symlink, or invalid surfaces;
- mutating repair apply is requested before write ownership and rollback semantics are approved.

Fallbacks must name executable next checks, not prose-only advice.

## Work Item Consumption

This contract is the stable output of #898 and #900. Later Work Items may move reserved commands to `implemented`, but they must preserve the command name, JSON result shape, and fail-closed behavior unless the parent FR records an explicit contract change.

## Installed Surface Diagnostics

`loom detect`, `loom doctor`, and `loom repair plan` implement the #888 detection layer.

`loom detect --target <repo> --json` reads only installation surfaces and classifies the target as:

- `uninstalled`
- `current`
- `legacy`
- `mixed`
- `mixed-legacy`

Detected surfaces are evidence, not authority by themselves. Legacy `.loom/bin`, repo-local `.agents/skills`, generated skills registries, plugin manifests, single-skill packages, installer status files, and symlinked surfaces must not be promoted to valid installed-state unless `loom-installed-state/v2` validates.

`loom doctor --target <repo> --json` consumes detection plus installed-state validation. It passes only when versioned installed-state is valid and no blocking legacy surface remains.

`loom repair plan --target <repo> --json` emits ordered non-mutating actions. `loom repair apply --target <repo> --json` currently fails closed and returns the plan because mutation ownership, rollback, and host adapter writes belong to later Work Items.

## Host Control Commands

`loom workspace`, `loom issue`, `loom project`, `loom pr`, `loom merge`, and `loom reconcile` implement the #893 control-plane command names.

These commands are thin CLI-first entries over host-owned truth. They read GitHub, git worktree, PR gate, controlled merge, and reconciliation evidence through existing Loom harness commands instead of creating another state source.

Stable schemas:

- `loom-workspace-control/v1` for workspace lifecycle wrappers.
- `loom-host-object-control/v1` for issue, project, PR, merge, and reconciliation wrappers.
- Existing delegated schemas such as `loom-pr-merge-gate/v1`, `loom-controlled-merge/v1`, and `loom-reconciliation-audit/v1` remain authoritative when the wrapper delegates to `loom_flow.py`.

Fail-closed conditions include missing issue or PR identifiers, unreadable GitHub state, fact-chain mismatch, dirty or ambiguous workspace state, stale PR head, missing Work Item binding, incomplete required checks, and mergeability drift.

Mutating actions require an explicit execution flag on the underlying command. `loom merge run` maps to controlled merge and requires `--apply` before `--execute` is passed to the host merge command. Reconciliation defaults to audit/dry-run semantics.

## Host Adapter Commands

`loom host list`, `loom host doctor`, `loom host install`, `loom host verify`, `loom host upgrade`, and `loom host remove` implement the #894 host orchestration surface with `loom-host-orchestration/v1`.

The CLI separates:

- Codex full-repo/native skills discovery as the default path.
- Adapter-managed plugin and single-skill installation through `loom-installer`.
- Contract-only hosts such as OpenCode, Gemini, and Cursor until adapter CLIs are available.

`host list` and `host doctor` are read-only. `host install` and `host upgrade` fail closed unless `--apply` is present and the built installer shim is available. `host remove` remains non-mutating in this phase and reports the missing rollback/delete ownership contract.

## Skills Commands

`loom skills list`, `loom skills generate`, `loom skills sync`, `loom skills check`, `loom skills doctor`, `loom skills package`, and `loom skills release-check` implement the #895 generated SKILLS surface with `loom-skills-surface/v1`.

`skills list` and `skills package` read checked-in generated package metadata. `skills check`, `skills doctor`, and `skills release-check` delegate to the existing surface, host adapter, and version checks. `skills generate` and `skills sync` mutate `skills/`, so they fail closed unless `--apply` is supplied.
