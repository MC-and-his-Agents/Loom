# Agent Harness Support Matrix

This retained path now owns the machine-readable support semantics for agent
harnesses. It does not claim that every external result source is an executable
adapter.

| Harness class | Support level | What Loom provides | What Loom does not claim |
| --- | --- | --- | --- |
| Codex | `native/primary` | Global Loom CLI, Codex plugin discovery, executable skills, session/tool mapping, verification, and real Codex CLI/App E2E | OS-level isolation from a malicious same-user process |
| Any harness that can reliably invoke the root `loom` CLI and consume JSON | `CLI-compatible` | The public 30-command CLI protocol | Plugin integration, session binding, tool mapping, or native E2E |
| A harness without a reliable CLI invocation path | `unsupported` | Documentation only | Installation, execution, discovery, or native integration |

Codex is the only `native/primary` harness in v0.32. Claude, Cursor, Gemini,
and OpenCode are not native Loom adapters. They may only be described as
`CLI-compatible` when the caller actually provides a reliable shell/CLI path;
otherwise they are `unsupported`.

Every harness consumes the same 30 public commands. Unsupported or removed
surfaces fail closed before Loom reads a target or provider state.

## Native admission

A future harness may become native only when all of these have an implemented
consumer and real E2E evidence:

- installation;
- discovery;
- execution;
- session binding;
- tool mapping;
- verification;
- real runtime E2E.

Protocol placeholders, retained JSON locators, documentation, or fixture-only
tests are insufficient.

## Codex install and refresh boundary

The Loom package is installed with npm:

```text
npm install -g @mc-and-his-agents/loom@latest
```

Codex owns its marketplace source and loaded plugin cache. Refreshing or
enabling the plugin is a structured Codex provider action, not a Loom CLI
command. After the provider action, use only public Loom readback commands:

```text
loom doctor --target <repo> --json
loom installed-state validate --target <repo> --json
loom verify --target <repo> --json
```

Start a new Codex session, or restart Codex Desktop when the plugin list or
runtime cache was already loaded. The retired host command family must not
appear as current remediation.

Repository adoption remains metadata-only. The target repository does not own
a repo-local runtime, plugin payload, current pointer, progress, review,
shadow, or ordinary closeout carrier.

## External result sources

`.loom/companion/interop.json#external_result_sources` may locate retained
results produced by another system. Loom only reads and validates the locator,
schema, binding, permission, result, and freshness. It does not call the source
or claim a native harness integration.

The former `host_adapters` field is removed. A v1 interop file receives one
`legacy_repo_interop_host_adapters` migration diagnostic per invocation and is
not silently consumed.

## Removed v1 matrix vocabulary

The v1 support matrix used these field identifiers:
`default_install_path`, `install_surface`, `discovery_surface`,
`bootstrap_or_session_start_surface`, `default_entry`,
`tool_mapping_surface`, `upgrade_surface`, `verification_surface`,
`fail_closed_conditions`, and `version_metadata_location`. They are retained
here only as a migration inventory; they are not an active schema and Loom does
not reconstruct a host adapter from them.

For Codex, the current entry remains `loom-init` and the generated distribution
path remains `plugins/loom/skills`. GitHub readback uses `gh api` through the
authenticated CLI keyring. `host_api_unreadable` is the typed failure when that
readback or its permission is unavailable; `CODEX_EXPORT_GH_TOKEN=1` remains an
explicit opt-in for a subprocess that cannot otherwise use the keyring.

## Version authority

The root package/release version, Codex plugin surface version, plugin payload
version/hash, skills registry version, and protocol schemas remain independent
authority lines. The historical `x-loom.host_adapter_version` manifest field is
the Codex plugin interface version; it is not a repo interop adapter claim.

## Fail closed

Loom reports one primary cause when:

- the public CLI or Codex plugin payload is absent or stale;
- a target, GitHub binding, permission, artifact, or external result locator is
  unreadable;
- an external result is stale, failing, unsafe, or bound to another head;
- a caller presents `host_adapters` instead of `external_result_sources`.

Provider/manual actions are separate structured fields. Every
`remediation_command` beginning with `loom` must resolve to one of the 30 public
commands.
