# loom-installed-state/v2

`loom-installed-state/v2` describes which Loom layers a target repository consumes. It is installation metadata, not backlog truth and not governance truth.
Artifact type, scope, authority, adoption mode, skills granularity, and
compatibility-mode terms are defined by
[installation-taxonomy.md](./installation-taxonomy.md).
The milestone #14 target state is defined by
[global-cli-user-plugin-contract.md](./global-cli-user-plugin-contract.md):
global CLI runtime provider, Codex user-level skills provider, and
metadata-only repository adoption.

The canonical target path is:

```text
.loom/installed-state.json
```

The CLI also reads `.loom/installed-state.v2.json` and `.loom/installed-state/installed-state.json` as compatibility paths.

## Required Shape

```json
{
  "schema_version": "loom-installed-state/v2",
  "installation_id": "repo-specific-stable-id",
  "contract": {
    "minimum_loom_version": "v0.28.0",
    "installed_state_schema": "loom-installed-state/v2"
  },
  "upgrade_eligibility": "current",
  "layers": [
    {
      "id": "adoption-metadata",
      "layer_type": "repository-adoption-metadata",
      "installed_path": ".loom/installed-state.json",
      "version_context": {
        "minimum_loom_contract": "v0.28.0",
        "installed_state_schema": "loom-installed-state/v2"
      },
      "runtime_state": "ready",
      "upgrade_eligibility": "current",
      "declared_support": {
        "suite_commands": [
          "suite inspect",
          "suite scaffold",
          "suite validate"
        ]
      },
      "provides": ["repository adoption truth"],
      "consumes": ["global-cli-provider", "user-skills-provider"]
    },
    {
      "id": "global-cli-provider",
      "layer_type": "global-cli-runtime-provider",
      "installed_path": "workstation:loom-cli",
      "version_context": {
        "provider": "loom-cli"
      },
      "runtime_state": "unknown",
      "upgrade_eligibility": "unknown",
      "provides": ["loom command semantics", "runtime provider"],
      "consumes": []
    },
    {
      "id": "user-skills-provider",
      "layer_type": "user-level-skills-provider",
      "installed_path": "workstation:codex-loom-plugin",
      "version_context": {
        "provider": "codex-loom-plugin"
      },
      "runtime_state": "unknown",
      "upgrade_eligibility": "unknown",
      "provides": ["Loom scenario skills"],
      "consumes": []
    }
  ],
  "installation_graph": {
    "layers": ["adoption-metadata", "global-cli-provider", "user-skills-provider"],
    "edges": [
      {"from": "adoption-metadata", "to": "global-cli-provider", "relationship": "requires-external-provider"},
      {"from": "adoption-metadata", "to": "user-skills-provider", "relationship": "requires-external-provider"}
    ]
  }
}
```

## Layers

Each layer must include:

- `id`
- `layer_type`
- `installed_path`
- `version_context`
- `runtime_state`: `ready`, `blocked`, or `unknown`
- `upgrade_eligibility`: `current`, `upgrade-available`, `drift`, `incompatible`, or `unknown`

`version_context` must be non-empty and must not contain missing or `unknown` values. If Loom cannot identify a layer's version authority, the layer is not safe to upgrade.

Non-ready layers must include:

- `failed_layer`
- `fail_closed_reason`

Layers or the top-level object may also include optional `declared_support`.
For the full spec suite CLI surface, Loom uses:

```json
{"suite_commands": ["suite inspect", "suite validate"]}
```

`declared_support` is a doctor/verify input only. It does not make suite CLI
output authoritative Work Item, review, merge-ready, closeout, or docs truth.
When suite command support is not declared, `loom doctor` does not require the
suite surface. When support is declared, `loom doctor` compares those command
names with `loom help --json` and fails closed if the command matrix is missing
commands or exposes the wrong domain/status/JSON capability.

Layers may also declare provider dependencies when the repository consumes an
external runtime/provider surface without owning it:

```json
{
  "provider_requirements": {
    "global_cli": {
      "required": true,
      "provider": "loom-cli",
      "authority": "workstation",
      "compatibility_mode_allowed": false
    }
  }
}
```

This dependency expresses a target-state boundary only: it allows diagnostics,
repair planning, and verification to explain that the repository depends on the
global CLI runtime provider. It does not make the workstation provider state
part of repository truth.

Targets may separately declare verify/profile requirements:

```json
{"profile_requirements": {"suite_validation": "required", "suite_item": "WI-1234"}}
```

`suite_validation` may be `required`, `blocking`, `full`, or `true`. `loom
verify` consumes this requirement, or an explicit `--item`, to run `suite
validate` as read-only gate evidence. Declared suite command support alone does
not make suite validation universally blocking.

## Installation Graph

`installation_graph.layers` lists layer ids. `installation_graph.edges` records dependency direction, typically:

```json
{"from": "skills", "to": "runtime", "relationship": "consumes"}
```

The graph exists so `loom upgrade`, `loom repair plan`, host adapters, source plugin payload generation, and installer shims can reason about layer ordering without reading unrelated governance files.
Every edge endpoint must reference a known layer id. Unknown edge endpoints fail closed because repair and upgrade ordering would otherwise be ambiguous.

## Codex Metadata-Only Mode

For downstream Codex, installed-state records metadata-only adoption and the
external user-level provider requirements. Repo-local embedded payload is legacy
migration input only.

### Metadata-Only Mode

Metadata-only adoption records repository adoption truth without requiring a
repo-embedded skills payload. The user-level Codex Loom plugin provides the
skills/provider surface, and workstation registration is verified separately
from repository truth:

```json
{
  "contract": {
    "minimum_loom_version": "v0.28.0",
    "installed_state_schema": "loom-installed-state/v2"
  },
  "runtime_provider": "global-cli",
  "repo_payload": {
    "mode": "metadata-only",
    "adoption_mode": "light-governance",
    "intentional_absent_paths": [
      ".loom/bin",
      ".loom/runtime",
      ".loom/tmp",
      ".loom/shadow",
      ".loom/status/current.md",
      ".loom/work-items",
      ".loom/progress",
      ".loom/specs",
      ".loom/reviews",
      "plugins/loom/.codex-plugin/plugin.json",
      "plugins/loom/skills",
      ".agents/skills",
      "skills"
    ]
  },
  "skills_provider": {
    "provider": "codex-loom-plugin",
    "scope": "user",
    "required": true,
    "registration_authority": "workstation"
  },
  "layers": [
    {
      "id": "adoption-metadata",
      "layer_type": "repository-adoption-metadata",
      "installed_path": ".loom/installed-state.json",
      "runtime_state": "ready",
      "upgrade_eligibility": "current",
      "provides": ["repository adoption truth"],
      "consumes": ["user-skills-provider"]
    },
    {
      "id": "user-skills-provider",
      "layer_type": "user-level-skills-provider",
      "installed_path": "workstation:codex-loom-plugin",
      "runtime_state": "unknown",
      "upgrade_eligibility": "unknown",
      "provides": ["Loom scenario skills"],
      "consumes": []
    }
  ],
  "installation_graph": {
    "layers": ["adoption-metadata", "user-skills-provider"],
    "edges": [
      {"from": "adoption-metadata", "to": "user-skills-provider", "relationship": "requires-external-provider"}
    ]
  }
}
```

`installed-state validate` validates repository metadata and mode semantics. It
must not fail metadata-only repositories merely because `plugins/loom/skills/`
is absent. `doctor`, `host verify`, and `skills check` report missing
workstation registration as a provider/workstation gap, not as missing
repository payload.

Installed-state is repository truth, not workstation state. New metadata-only
records must not write top-level `target`, `installed_at`, `upgraded_at`,
`cli_freshness`, `plugin_freshness`, `plugin_cache_path`, or
`host_machine_path`. Upgrades should remove those fields when refreshing the
repo contract.

When metadata-only repositories also depend on the global CLI runtime provider,
installed-state must keep the two dependencies separate:

- repository truth records the dependency in metadata;
- workstation/user plugin registration remains a workstation-truth check;
- global CLI runtime availability remains a provider/runtime check;
- neither check may be rewritten as embedded repository payload drift.

### Legacy Embedded Payload Mode

Embedded payload mode is legacy repository payload state. It is diagnosable
migration input, not the milestone #14 current install target:

```json
{
  "layers": [
    {
      "id": "runtime",
      "layer_type": "full-repo-runtime",
      "installed_path": ".loom/bin"
    },
    {
      "id": "plugin-embedded-skills",
      "layer_type": "plugin-embedded-skills",
      "installed_path": "plugins/loom/skills",
      "consumes": ["runtime"]
    },
    {
      "id": "host-adapter",
      "layer_type": "host-adapter-plugin",
      "installed_path": "plugins/loom",
      "consumes": ["plugin-embedded-skills"]
    }
  ],
  "installation_graph": {
    "layers": ["runtime", "plugin-embedded-skills", "host-adapter"],
    "edges": [
      {"from": "plugin-embedded-skills", "to": "runtime", "relationship": "consumes"},
      {"from": "host-adapter", "to": "plugin-embedded-skills", "relationship": "consumes"}
    ]
  }
}
```

Current downstream adoption must not create these layers. If they exist, Loom
diagnostics treat them as unsupported legacy residue or target-owned surface
until ownership is proven. Repair and upgrade plans must not delete or overwrite
target-owned non-Loom skills automatically.

`.agents/skills` is likewise a compatibility export surface, not a default Loom
downstream layer.

## Legacy Repo-Local Wrapper And Global CLI Provider

Installed-state may describe legacy repositories that still carry a repo-local
wrapper while the active runtime/provider is the global CLI:

```json
{
  "provider_requirements": {
    "global_cli": {
      "required": true,
      "provider": "loom-cli",
      "authority": "workstation",
      "compatibility_mode_allowed": true
    }
  },
  "layers": [
    {
      "id": "repo-local-wrapper",
      "layer_type": "repo-local-wrapper",
      "installed_path": ".loom/bin",
      "runtime_state": "ready",
      "upgrade_eligibility": "current",
      "provides": ["compatibility starter aliases"],
      "consumes": ["global-cli-provider"]
    },
    {
      "id": "global-cli-provider",
      "layer_type": "global-cli-runtime-provider",
      "installed_path": "workstation:loom-cli",
      "runtime_state": "unknown",
      "upgrade_eligibility": "unknown",
      "provides": ["loom command semantics", "runtime provider"],
      "consumes": []
    }
  ],
  "installation_graph": {
    "layers": ["repo-local-wrapper", "global-cli-provider"],
    "edges": [
      {"from": "repo-local-wrapper", "to": "global-cli-provider", "relationship": "delegates-to-provider"}
    ]
  }
}
```

This legacy mode means:

- `.loom/bin` may remain present as migration residue;
- the wrapper does not become the authority for runtime/provider version truth;
- the global CLI provider remains external workstation/user state;
- diagnostics must explain whether a failure belongs to wrapper residue,
  provider availability, or repository metadata drift.

Detected `.loom/bin` by itself is still only a hint. For the milestone #14 target
it blocks as unsupported legacy residue until migration or cleanup resolves it.

### Global CLI Without Repo-Local Wrapper

A `global-cli` repository may omit `.loom/bin` entirely. In that mode,
installed-state records repository adoption truth and provider requirements,
while the root `loom` executable and its packaged runtime remain external
workstation/user-level provider state:

```json
{
  "provider_requirements": {
    "global_cli": {
      "required": true,
      "provider": "loom-cli",
      "authority": "workstation",
      "compatibility_mode_allowed": false
    }
  },
  "layers": [
    {
      "id": "adoption-metadata",
      "layer_type": "repository-adoption-metadata",
      "installed_path": ".loom/installed-state.json",
      "runtime_state": "ready",
      "upgrade_eligibility": "current",
      "provides": ["repository adoption truth"],
      "consumes": ["global-cli-provider"]
    },
    {
      "id": "global-cli-provider",
      "layer_type": "global-cli-runtime-provider",
      "installed_path": "workstation:loom-cli",
      "runtime_state": "unknown",
      "upgrade_eligibility": "unknown",
      "provides": ["loom command semantics", "runtime provider"],
      "consumes": []
    }
  ],
  "installation_graph": {
    "layers": ["adoption-metadata", "global-cli-provider"],
    "edges": [
      {"from": "adoption-metadata", "to": "global-cli-provider", "relationship": "requires-external-provider"}
    ]
  }
}
```

Copyable validation commands for this mode:

```bash
loom installed-state validate --target . --json
loom detect --target . --json
loom doctor --target . --json
loom verify --target . --json
loom repair plan --target . --json
```

Passing repository metadata validation does not prove that every developer
workstation has the global CLI installed. `doctor` and `verify` diagnose that
external provider boundary; their output must not copy local workstation paths,
cache state, or registration outcomes into repository truth.

## Compatibility Mode

Compatibility mode is valid installed-state only when the metadata says so. It
is not inferred from legacy residue alone.

Typical legacy compatibility-mode cases:

- a repo-local wrapper remains while execution is delegated to the global CLI
  runtime provider;
- `.loom/bin` is retained for audit or gate parity but is not the active
  provider;
- workstation/provider registration is required but separate from repository
  truth.

Compatibility mode must stay diagnosable:

- `installed-state validate` checks that repository metadata is internally
  coherent;
- `doctor` explains whether the gap is repository truth, provider/runtime, or
  workstation registration;
- `verify` consumes the same boundary and must not silently convert provider
  gaps into repository payload success.

## CLI Semantics

```bash
loom installed-state validate --target <repo> --json
loom detect --target <repo> --json
loom doctor --target <repo> --json
```

These public commands fail closed when metadata is missing, unreadable, or invalid. Missing metadata may include `legacy_surface_hints` such as `.loom/bin`, `.agents/skills`, `skills/registry.json`, plugin manifests, or old installer status files. Those hints are diagnostic input for `loom detect`, `loom doctor`, and `loom repair plan`; they are not treated as valid installed-state by themselves.

`loom detect --target <repo> --json` may report legacy or mixed surfaces even when installed-state is missing. This is a diagnostic pass, not an install-state pass. `loom doctor` turns missing, invalid, legacy, or mixed surfaces into `result: block` with `fallback_to: ["loom repair plan"]`. `loom repair plan` is non-mutating; an admitted write path is `loom upgrade --apply`.

When installed-state declares `runtime_provider: global-cli` but a repository
still retains `.loom/bin`, repair and upgrade planning must treat that path as
runtime-carrier residue, not as plugin payload drift or current provider proof.
The non-mutating plan must:

- keep runtime-carrier migration separate from skills/plugin payload migration;
- enumerate repo-local gate blockers that still reference `.loom/bin`, including
  exact carrier locators when deletion is not yet safe to propose;
- keep retained `.loom/bin` deletion proposal-only until an explicit
  apply/confirmation contract is approved.

The target-state boundary for migration, `doctor`, and `verify` is therefore:

- repository truth must explicitly model whether a repo-local wrapper is
  current, retained, audit-only, obsolete, or compatibility-only;
- repository truth may declare a dependency on the global CLI runtime provider
  or a workstation/user-level skills provider without owning either one;
- stale `.loom/bin`, mixed legacy surfaces, or missing provider state remain
  diagnosable blocking outputs until the declared target state is satisfied;
- diagnostics must identify which authority owns the next action instead of
  collapsing all failures into generic repository drift.

## Work Item Consumption

This contract is the stable output of #902 and #903. `installed-state show|validate|export` implements the first CLI consumer for #904, with fixture coverage for missing metadata, legacy surfaces, valid graph export, and mixed/unknown version metadata for #905.
