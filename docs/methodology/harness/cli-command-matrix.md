# Loom CLI Command Matrix

## v0.31 Default Product Surface

Loom v0.31 exposes exactly 30 public commands. They form the only supported
default product surface and are owned by 12 generic protocol types:

1. manifest
2. locator
3. observation
4. delivery verdict
5. product acceptance
6. reconciliation verdict
7. review attestation
8. host attestation
9. failure envelope
10. migration plan
11. release judgment
12. readback

The 96 commands in `LEGACY_COMMAND_INVENTORY` are removed, not hidden aliases.
Every legacy invocation is rejected before target resolution, GitHub readback,
subprocess dispatch, or mutation. A profile, governance intensity, compatibility
flag, stale installed-state declaration, or repository carrier cannot re-enable
one of those commands.

The machine-readable authority is:

```bash
loom help --json
```

Maintainers in the Loom source checkout may use
`python3 tools/loom.py help --json`. Downstream users use the installed global
CLI.

## Public Commands

| Command | Owner area | Product contract |
| --- | --- | --- |
| `loom version` | core | Read CLI, source, distribution, plugin, and package version context. |
| `loom help` | core | Read task routes and the public command matrix. |
| `loom acceptance resolve` | acceptance | Resolve authenticated product-acceptance evidence without owning product truth. |
| `loom attestation readback` | host attestation | Read current-head review and workflow proof from GitHub. |
| `loom attestation closeout` | host attestation | Read host-native Work Item closeout without repository carriers. |
| `loom installed-state validate` | installation | Validate the metadata-only installation manifest and provider declarations. |
| `loom detect` | diagnostics | Detect supported installation surfaces and unsupported legacy residue. |
| `loom doctor` | diagnostics | Diagnose adoption, provider readiness, and unsupported residue. |
| `loom repair plan` | repair | Emit a read-only repair plan; it never applies changes. |
| `loom install` | delivery | Install metadata-only repository adoption with explicit `--apply`. |
| `loom upgrade` | delivery | Plan v0.30→v0.31 migration by default; mutate only with explicit `--apply`. |
| `loom verify` | delivery | Verify the supported metadata-only/global-provider boundary. |
| `loom route` | scenario | Plan or admit an issue through host-native lifecycle facts. |
| `loom status` | harness | Derive current state from explicit inputs, worktree, and host facts. |
| `loom profile status` | profile | Read the active profile and its enforced invariants. |
| `loom profile light-migration-reconcile` | profile | Reconcile light-profile required checks and main-tree readback. |
| `loom story` | scenario | Prepare product story/readiness context without creating execution carriers. |
| `loom build` | scenario | Admit implementation for an explicit Work Item and branch before a PR exists. |
| `loom pre-review` | scenario | Verify PR/Work Item/host bindings before semantic review. |
| `loom review` | scenario | Produce or consume host-native current-head semantic review proof. |
| `loom merge-ready` | scenario | Read host facts, attestation, and gate verdict for the current PR head. |
| `loom closeout` | scenario | Check host-native closeout readiness. |
| `loom release readback` | delivery | Read tag, Release, npm, workflow, version, and commit consistency. |
| `loom workspace create` | host control | Create an issue-scoped local worktree. |
| `loom workspace check` | host control | Verify Work Item, branch, worktree, PR, and head binding when applicable. |
| `loom workspace retire` | host control | Retire only the local worksite; do not write repository closeout state. |
| `loom pr gate` | host control | Read the retained PR gate verdict for an explicit PR head and Work Item. |
| `loom merge check` | delivery | Run read-only controlled-merge preflight against current host facts. |
| `loom merge run` | delivery | Merge through the host only after same-head `merge check` passes and `--apply` is explicit. |
| `loom ship` | delivery | Orchestrate admission, host bindings, attestation, gate, merge, validation, and host-only closeout. |

Scenario skill names such as `loom-init`, `loom-adopt`, and `loom-build` are
agent interaction entrypoints. They are not additional CLI commands.

## Default Lifecycle

The ordinary lifecycle is:

```text
route
  -> build (explicit Work Item + branch; PR may not exist yet)
  -> pre-review (real PR required)
  -> review / attestation readback
  -> merge-ready or merge check
  -> ship or merge run
  -> attestation closeout
  -> workspace retire
```

Planning FRs may exist without Work Items. Once implementation starts, `build`
requires an explicit Work Item and branch, but it must not require a diff, empty
commit, empty PR, repo current pointer, progress file, review file, shadow, or
closeout carrier. PR-dependent commands require a real PR only when that stage
is reached.

`ship` stays host-native and ordered:

```text
lifecycle admission
  -> host bindings
  -> review attestation
  -> PR gate
  -> controlled merge
  -> changed-path validation profile
  -> host-only closeout policy
```

Release source changes still use an ordinary reviewed PR and release workflow.
After publishing, `release readback` is terminal. It creates no closeout-only or
current-retire PR.

## Removed-State Contract

Removed legacy invocations return one failure envelope with:

```text
primary_error_code: unsupported_command_surface
failure_domain: toolchain
owner: loom
retryable: false
remediation_command: loom help --json
target_read: false
host_read: false
mutation_attempted: false
```

Removed-state tests assert absence. They must not preserve a legacy handler,
schema, policy, fixture, help entry, or positive checker assertion merely to
test migration history. Historical behavior remains available through Git and
release history.

An older installed-state manifest may name a removed provider probe. Validation
maps only the three supported declarations to public replacements:

| Removed declaration | Public replacement |
| --- | --- |
| `fact-chain` | `status` |
| `shadow-parity` | `verify` |
| `workstation current` | `status` |

This mapping is input normalization, not a callable compatibility decoder.

## Output And Failure Contract

Agent-facing `--json` output is direct JSON when it fits the effective stdout
budget. Larger diagnostics return a compact summary plus an artifact locator.
`--full-output` is for explicit debugging and audit, not routine handoff text.

Every failed public command exposes exactly one primary cause. Consequential
findings remain nested. v0.31 specifically distinguishes:

| Condition | Primary code | Domain | Owner |
| --- | --- | --- | --- |
| A removed current pointer is still treated as authoritative | `legacy_current_pointer_dependency` | carrier | loom |
| Build requires a PR that cannot exist before build | `pre_pr_build_admission_cycle` | toolchain | loom |
| Current GitHub host facts cannot be read | `github_host_readback_failure` | host_service | github |

This release does not attempt a repository-wide failure-taxonomy rewrite.

## Mutation Boundary

Read-only is the default. Commands that can change repository or host state
require explicit `--apply`, bind the action to current inputs, and read back the
result. `repair plan`, `status`, `detect`, `doctor`, `verify`, `merge check`, and
`release readback` never mutate. Removed commands are rejected before any read
or mutation boundary.

Ordinary delivery writes no `.loom/status/current.md`, `.loom/progress/**`,
`.loom/reviews/**`, shadow, or closeout carrier. Reinforced governance may
increase review or validation strength, but it cannot restore those removed
surfaces.
