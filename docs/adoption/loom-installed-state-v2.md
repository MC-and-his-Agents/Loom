# loom-installed-state/v2

`loom-installed-state/v2` describes which Loom layers a target repository consumes. It is installation metadata, not backlog truth and not governance truth.

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
  "target": "/absolute/or/repo-relative/target",
  "upgrade_eligibility": "current",
  "layers": [
    {
      "id": "runtime",
      "layer_type": "full-repo-runtime",
      "installed_path": ".loom/bin",
      "version_context": {
        "repo_version": "v0.13.0",
        "runtime_core_version": "1.0.0"
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
      "provides": ["loom runtime wrappers"],
      "consumes": []
    }
  ],
  "installation_graph": {
    "layers": ["runtime"],
    "edges": []
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

## Installation Graph

`installation_graph.layers` lists layer ids. `installation_graph.edges` records dependency direction, typically:

```json
{"from": "skills", "to": "runtime", "relationship": "consumes"}
```

The graph exists so `loom upgrade-plan`, `loom repair plan`, host adapters, skills sync, and installer shims can reason about layer ordering without reading unrelated governance files.
Every edge endpoint must reference a known layer id. Unknown edge endpoints fail closed because repair and upgrade ordering would otherwise be ambiguous.

## CLI Semantics

```bash
python3 tools/loom.py installed-state show --target <repo> --json
python3 tools/loom.py installed-state validate --target <repo> --json
python3 tools/loom.py installed-state export --target <repo> --json
```

All three commands fail closed when metadata is missing, unreadable, or invalid. Missing metadata may include `legacy_surface_hints` such as `.loom/bin`, `.agents/skills`, `skills/registry.json`, plugin manifests, or old installer status files. Those hints are diagnostic input for `loom detect`, `loom doctor`, and `loom repair plan`; they are not treated as valid installed-state by themselves.

`loom detect --target <repo> --json` may report legacy or mixed surfaces even when installed-state is missing. This is a diagnostic pass, not an install-state pass. `loom doctor` turns missing, invalid, legacy, or mixed surfaces into `result: block` with `fallback_to: ["loom repair plan"]`. `loom repair plan` is non-mutating. `loom repair apply` remains fail-closed until a later Work Item approves write ownership and rollback semantics.

## Work Item Consumption

This contract is the stable output of #902 and #903. `installed-state show|validate|export` implements the first CLI consumer for #904, with fixture coverage for missing metadata, legacy surfaces, valid graph export, and mixed/unknown version metadata for #905.
