# Version Authority Map

Loom does not use one global version number for every distribution surface. Versions are not globally synchronized.

The Loom CLI release version, installer package version, plugin surface version, host adapter version, plugin payload version, plugin payload hash, skills registry version, contract version, and schema version are separate authority lines.

Target repository release / version truth is also separate from Loom's own distribution version lines. Loom may read a target repository release target through repo companion locators, but it must not infer that a target release id, `VERSION`, installer version, plugin version, runtime version, or schema version are the same thing.

## Authority Lines

| Surface | Authority | Synchronization rule |
| --- | --- | --- |
| Loom CLI release candidate | `VERSION` | Declares the primary CLI-first release candidate line for the root repository. It may be ahead of the latest published GitHub release. |
| Published Loom CLI release | GitHub `v*` tag and release | Represents published `loom` CLI / root runtime release truth. The tag must point at the release commit. |
| Root Loom CLI npm package | `@mc-and-his-agents/loom` package version | User-facing npm install channel for the root `loom` CLI. The npm version is derived from root `VERSION` by removing the leading `v`, and publish closeout must reconcile it with the matching GitHub `v*` tag and release. |
| Target repository release target | repo-owned or host-owned release object locator | Represents the target repository's own delivery/release truth, not Loom distribution metadata. |
| Deprecated installer legacy artifact | npm `@mc-and-his-agents/loom-installer@0.1.119` / tag `loom-installer-v0.1.119` | Historical host locator only. No installer tombstone remains in the source tree; this is not a current CLI, recommended install path, active release line, or Loom CLI release evidence. |
| Plugin surface version | host plugin manifest, currently `plugins/loom/.codex-plugin/plugin.json` | Version of the Codex plugin interface and adapter surface. It changes only when the host-facing plugin surface changes, not when Loom skills content changes. |
| Host adapter version | plugin metadata `x-loom.host_adapter_version` or adapter manifest | Version of host wiring semantics. |
| Plugin payload version | plugin release metadata, primarily `plugins/loom/.codex-plugin/plugin.json` `x-loom.plugin_payload_version` | Version of the installable `plugins/loom` payload. It follows the root Loom release / npm package version, for example `0.19.0`. |
| Plugin payload hash | plugin release metadata, primarily `plugins/loom/.codex-plugin/plugin.json` `x-loom.plugin_payload_hash` | Deterministic SHA-256 of the installable `plugins/loom` payload used to decide whether a source, marketplace entry, or runtime cache is fresh. |
| Skills registry version | `plugins/loom/skills/registry.json` `registry_version`; mirrored by `skills/registry.json` while the root mirror remains checked in | Version of the generated skills registry/index format and payload entry set. It is not the installed payload freshness authority. |
| Skill contract version | `skills/<skill-id>/contract.json` `contract_version` | Version of the named skill behavioral contract. It is not a single-skill distribution version and does not decide plugin payload freshness by itself. |
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

The plugin payload release metadata may be carried by the plugin manifest under
`x-loom`, or by an adjacent release metadata manifest used by host install and
readback:

```text
source_package
source_package_version
source_git_sha
plugin_payload_version
plugin_payload_hash
```

`source_package` is `@mc-and-his-agents/loom`. `source_package_version` and
`plugin_payload_version` follow the root Loom npm package version for the
release that produced the payload. `source_git_sha` records the release commit
that produced the payload. The authoritative hash carrier must avoid
self-reference: either keep `plugin_payload_hash` in metadata outside the digest
root, or normalize/exclude only the `plugin_payload_hash` field while computing
the digest.

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
- plugin install compares plugin surface and host adapter versions for compatibility, then compares plugin payload version/hash for freshness
- single-skill install is not a current Loom distribution surface
- installer upgrade compares npm package version only for legacy status reporting and must not make installer `latest` the current Loom CLI version

No check may infer that `VERSION`, plugin surface version, installer version, skills registry version, contract version, and schema version must be equal.
No check may use `registry_version`, `contract_version`, or legacy `skill_package_version` as the plugin payload freshness authority.
No check may infer that a `loom-installer-v*` tag publishes the `loom` CLI.
No check may recommend `@mc-and-his-agents/loom-installer` or `npx loom-installer` as the current Loom install path.
No check may infer that a target repository release target is the same authority line as Loom's `VERSION`, installer version, plugin version, runtime version, or skill contract/schema version.

## Plugin Payload Hash Rule

`plugin_payload_hash` is a SHA-256 digest over the installable `plugins/loom`
payload:

1. Walk all payload files under `plugins/loom`.
2. Ignore `.DS_Store`, `__pycache__`, and `*.pyc`.
3. If the hash carrier is stored inside the walked tree, normalize or exclude
   only the self-referential `plugin_payload_hash` field from the digest input.
   Other release metadata fields remain part of the payload evidence.
4. Sort file paths by their POSIX relative path from `plugins/loom`.
5. For each file, append `relative_path`, a NUL byte, the raw file bytes, and a
   NUL byte to the digest input.
6. Encode the final SHA-256 digest as lowercase hexadecimal.

The traversal order must not affect the digest. Any non-ignored payload file
change outside the normalized self-referential hash field must change the
digest.

## Failure Rule

If version metadata is missing, unreadable, or inconsistent with the installed layer, the host or installer must report a fail-closed state instead of a partial success.
