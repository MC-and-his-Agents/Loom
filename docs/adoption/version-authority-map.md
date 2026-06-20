# Version Authority Map

Loom does not use one global version number for every distribution surface. Versions are not globally synchronized.

The Loom CLI release version, installer package version, plugin surface version, host adapter version, plugin payload registry_version, contract version, and schema version are separate authority lines.

Target repository release / version truth is also separate from Loom's own distribution version lines. Loom may read a target repository release target through repo companion locators, but it must not infer that a target release id, `VERSION`, installer version, plugin version, runtime version, or schema version are the same thing.

## Authority Lines

| Surface | Authority | Synchronization rule |
| --- | --- | --- |
| Loom CLI release candidate | `VERSION` | Declares the primary CLI-first release candidate line for the root repository. It may be ahead of the latest published GitHub release. |
| Published Loom CLI release | GitHub `v*` tag and release | Represents published `loom` CLI / root runtime release truth. The tag must point at the release commit. |
| Root Loom CLI npm package | `@mc-and-his-agents/loom` package version | User-facing npm install channel for the root `loom` CLI. The npm version is derived from root `VERSION` by removing the leading `v`, and publish closeout must reconcile it with the matching GitHub `v*` tag and release. |
| Target repository release target | repo-owned or host-owned release object locator | Represents the target repository's own delivery/release truth, not Loom distribution metadata. |
| Deprecated installer legacy artifact | `packages/loom-installer/package.json` | Historical npm package metadata only. The last active baseline is `@mc-and-his-agents/loom-installer` `0.1.119` / `loom-installer-v0.1.119`. It is not a current CLI, recommended install path, active release line, or evidence that the `loom` CLI was published. |
| Plugin surface version | host plugin manifest, currently `plugins/loom/.codex-plugin/plugin.json` | Version of the plugin adapter surface, not the Loom repo version. |
| Host adapter version | plugin metadata `x-loom.host_adapter_version` or adapter manifest | Version of host wiring semantics. |
| Skill contract version | `skills/<skill-id>/contract.json` `contract_version` | Version of the named skill behavioral contract. |
| Plugin payload registry_version | `plugins/loom/skills/registry.json` `registry_version` | Version of the Codex user plugin skills payload generated from `src/skills/`. |
| Skills registry version | `skills/registry.json` `registry_version` | Compatibility mirror of the plugin payload registry version while root `skills/` remains checked in. |
| External runtime schema version | external runtime locator `schema_version` | Protocol/schema version for adopted repos consuming external runtime. |

## Machine-Readable Metadata

The Codex user plugin payload exposes version context in:

```text
plugins/loom/skills/registry.json
```

The plugin surface exposes adapter version context in:

```text
plugins/loom/.codex-plugin/plugin.json
```

The installer payload exposes aggregate version context in:

```text
packages/loom-installer/payload/manifest.json
```

The `loom` CLI release surface is defined in:

```text
docs/adoption/loom-cli-release-surface.md
```

The CLI-only user install contract is defined in:

```text
docs/adoption/cli-only-install-contract.md
```

## Upgrade Rule

Upgrades compare the version surface relevant to the installed layer:

- full repo install is legacy and must not be used as a current version authority
- `loom` CLI release compares `VERSION` plus the GitHub `v*` tag and Release state
- root `loom` CLI npm install compares `@mc-and-his-agents/loom` package version plus the GitHub `v*` tag and Release state
- plugin install compares plugin surface, host adapter versions, and plugin payload registry_version
- single-skill install is not a current Loom distribution surface
- installer upgrade compares npm package version only for legacy status reporting and must not make installer `latest` the current Loom CLI version

No check may infer that `VERSION`, plugin version, installer version, contract version, and schema version must be equal.
No check may infer that a `loom-installer-v*` tag publishes the `loom` CLI.
No check may recommend `@mc-and-his-agents/loom-installer` or `npx loom-installer` as the current Loom install path.
No check may infer that a target repository release target is the same authority line as Loom's `VERSION`, installer version, plugin version, runtime version, or skill contract/schema version.

## Failure Rule

If version metadata is missing, unreadable, or inconsistent with the installed layer, the host or installer must report a fail-closed state instead of a partial success.
