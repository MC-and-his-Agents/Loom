# Version Authority Map

Loom does not use one global version number for every distribution surface. Versions are not globally synchronized.

The installer package version, plugin surface version, host adapter version, skill package version, contract version, and schema version are separate authority lines.

Target repository release / version truth is also separate from Loom's own distribution version lines. Loom may read a target repository release target through repo companion locators, but it must not infer that a target release id, `VERSION`, installer version, plugin version, runtime version, or schema version are the same thing.

## Authority Lines

| Surface | Authority | Synchronization rule |
| --- | --- | --- |
| Repository release candidate | `VERSION` | Declares the repo candidate line. It may be ahead of the latest published GitHub release. |
| Published repository release | GitHub `v*` tag and release | Represents published root repo release truth. |
| Target repository release target | repo-owned or host-owned release object locator | Represents the target repository's own delivery/release truth, not Loom distribution metadata. |
| Installer package version | `packages/loom-installer/package.json` | Independent npm package line. Published with `loom-installer-v<version>` tags. |
| Plugin surface version | host plugin manifest, currently `plugins/loom/.codex-plugin/plugin.json` | Version of the plugin adapter surface, not the Loom repo version. |
| Host adapter version | plugin metadata `x-loom.host_adapter_version` or adapter manifest | Version of host wiring semantics. |
| Generated skill package version | `skills/<skill-id>/loom-package.json` `skill_package_version` | Version of the generated single-skill package surface. |
| Skill contract version | `skills/<skill-id>/contract.json` `contract_version` | Version of the named skill behavioral contract. |
| Skills registry version | `skills/registry.json` `registry_version` | Version of the full generated skills registry. |
| Runtime core version | `skills/<skill-id>/loom-package.json` `runtime_core_version` | Version of the package-internal runtime closure. |
| External runtime schema version | external runtime locator `schema_version` | Protocol/schema version for adopted repos consuming external runtime. |

## Machine-Readable Metadata

Each generated single-skill package exposes version context in:

```text
skills/<skill-id>/loom-package.json
```

The plugin surface exposes adapter version context in:

```text
plugins/loom/.codex-plugin/plugin.json
```

The installer payload exposes aggregate version context in:

```text
packages/loom-installer/payload/manifest.json
```

## Upgrade Rule

Upgrades compare the version surface relevant to the installed layer:

- full repo install compares repository revision plus generated `skills/` metadata
- plugin install compares plugin surface and host adapter versions
- single-skill install compares `skill_package_version`, `skill_contract_version`, `runtime_core_version`, and `source_revision`
- installer upgrade compares npm package version

No check may infer that `VERSION`, plugin version, installer version, contract version, and schema version must be equal.
No check may infer that a target repository release target is the same authority line as Loom's `VERSION`, installer version, plugin version, runtime version, or skill contract/schema version.

## Failure Rule

If version metadata is missing, unreadable, or inconsistent with the installed layer, the host or installer must report a fail-closed state instead of a partial success.
