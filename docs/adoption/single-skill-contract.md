# Single-Skill Contract

This contract applies to every generated `skills/<skill-id>` directory.

`src/skills/<skill-id>` is the editable source truth. Root `skills/<skill-id>` is the checked-in generated package consumed by host-native discovery and generic single-skill installers.

## Package Shape

Each generated package must contain:

- `SKILL.md`
- `contract.json`
- `loom-package.json`
- `scripts/<skill-id>.py`
- `references/` when the skill has local references
- `agents/` when the skill has adapter metadata
- `.loom-runtime/`

The package must be installable by copying the single `skills/<skill-id>` directory into a host skill directory.

The copied directory must be sufficient on its own. A valid single-skill package must not require the Loom repository root, `src/skills/`, `skills/shared/`, or sibling generated skill directories at runtime.

## Runtime Root

The package runtime root is `.loom-runtime/`. Launchers must set `LOOM_INSTALLED_SKILLS_ROOT` to that package-internal runtime root before entering shared runtime code.

Generated top-level package files must not require sibling paths such as `../shared`, `../registry.json`, or another generated skill directory.

## Metadata

`loom-package.json` is the machine-readable package contract. It must include:

- `schema_version`
- `package_type`
- `package_id`
- `repo_version`
- `source_repository`
- `source_revision`
- `skill_package_version`
- `skill_contract_version`
- `registry_version`
- `runtime_core_version`
- `runtime_root`
- `launcher`
- `root_entry`
- `plugin_surface_version`
- `host_adapter_version`
- `full_repo_install_surface`
- `fail_closed_on`

For generated single-skill packages, `package_type` must be `single-skill`, `runtime_root` must be `.loom-runtime`, and `full_repo_install_surface` must be `false`.

## Behavior Boundary

A single-skill install exposes only the named skill. It does not expose the full Loom scenario surface and must not claim that `loom-init` routing is available unless the installed package is `loom-init`.

Even when the installed package is `loom-init`, the host has installed only the `loom-init` package. That package may route conceptually, but the host must not claim the rest of the Loom scenario skills are installed unless the full generated `skills/` surface is also available through full repo install.

## Fail-Closed Rules

The package must fail closed when:

- required files are missing
- launcher is missing or not executable
- `.loom-runtime/` is missing
- `.loom-runtime/registry.json`, `install-layout.json`, or `upgrade-contract.json` is missing
- top-level package files reference paths outside the package
- runtime-state cannot report `installed-runtime`
- version metadata is unreadable or inconsistent with `contract.json`

## Verification

Run:

```bash
make skills-check
```

This checks generated drift, package completeness, package-external references, launcher runtime-state, and generic skill-installer compatibility shape.

The version authority for `loom-package.json` fields is defined in [version-authority-map.md](./version-authority-map.md).
