# Loom Installation Taxonomy

This document is the authoritative Loom installation taxonomy for artifact
type, scope, authority, and skills granularity. Other adoption, installed-state,
CLI, and host-adapter documents should reference this contract instead of
redefining install meanings.

The milestone #14 downstream target is defined by
[global-cli-user-plugin-contract.md](./global-cli-user-plugin-contract.md):
global `loom` CLI, Codex user-level Loom plugin, and metadata-only repository
adoption. Repo-local runtime, repo-local plugin payload, and single-skill
distribution are legacy surfaces for detection and migration only.

## Authority Boundaries

Loom separates repository truth from workstation truth:

| Authority | Scope | Owns | Does not own |
| --- | --- | --- | --- |
| Repository adoption truth | Versioned target repository | `.loom/installed-state.json` and equivalent compatibility paths | Codex Desktop registration, user plugin cache, personal marketplace entries |
| Repo-owned governance residue | Versioned target repository | `.loom/companion`, repo interop metadata, evidence carriers, repo-native gates and closeout evidence | Loom plugin payload ownership or workstation discovery |
| Global CLI runtime provider | User/workstation executable plus its shipped runtime | The `loom` command semantics, packaged runtime/provider version, and external provider provenance | Repository adoption truth, repo-owned governance residue, or workstation registration truth |
| Published plugin marketplace catalog | Loom source repository | A deterministic catalog that advertises the packaged Loom Codex plugin, such as `.agents/plugins/marketplace.json` pointing to `./plugins/loom` | User/workstation plugin installation state, Codex runtime cache, or downstream repository adoption truth |
| Embedded repository payload | Versioned target repository, legacy residue | `plugins/loom/.codex-plugin/plugin.json` and `plugins/loom/skills/` | User-level Codex plugin registration |
| Workstation registration truth | User workstation | Codex personal marketplace entry, user plugin cache, Codex config enablement | Repository adoption truth or repo-owned governance evidence |
| Compatibility export | Explicit export target | `.agents/skills` or another host compatibility surface selected by the operator | Default Loom downstream adoption |
| Host repository namespace | Target repository | Root `skills/` when the target repository owns skills | Loom-generated downstream skills by default |

The user-level Codex Loom plugin is a skills/provider surface. Its registration
state is workstation truth. A repository may depend on that provider in
installed-state, but the repository must not record the workstation registration
itself as repository truth.

The root `loom` CLI is also a provider surface. When a repository consumes the
global CLI runtime provider, repository truth may declare that dependency, but
it must not copy user/workstation provider state, provider cache paths, or
registration outcomes into versioned repository truth.

A published plugin marketplace catalog is source distribution metadata, not an
installed-state record. The Loom source repository may version a deterministic
catalog only when it points the `loom` plugin at the source payload
`./plugins/loom` and contains no workstation installed-state or runtime-cache
fields. Downstream repositories must not use `.agents/plugins/marketplace.json`
to record Codex plugin installation or registration state.

## Artifact Types

Loom install and verify commands must classify artifacts before mutating or
diagnosing them:

| Artifact type | Default scope | Authority | Notes |
| --- | --- | --- | --- |
| Installed-state metadata | Repository | Repository adoption truth | Records the chosen adoption mode and layer graph. |
| Repo companion / interop / evidence | Repository | Repo-owned governance residue | Preserved across plugin and provider changes. |
| Global CLI runtime provider | User/workstation | Global CLI runtime provider | The default CLI-owned provider surface for `loom` command semantics and shipped runtime. |
| Published plugin marketplace catalog | Source repository | Distribution catalog | Advertises `plugins/loom` as an installable Codex plugin source; not valid as downstream installed-state. |
| Host adapter plugin manifest | Repository or user plugin source | Embedded repository payload or workstation provider | Repository copy is only required in embedded payload mode. |
| Plugin-embedded skills bundle | Repository | Legacy embedded repository payload | `plugins/loom/skills/` is unsupported legacy residue for the milestone #14 target. |
| User-level skills provider | Workstation | Workstation registration truth | Used by metadata-only adoption; verified separately from repo truth. |
| Full Loom skills bundle export | Compatibility export | Compatibility/discovery surface | Explicit opt-in; never the default metadata-only surface. |
| Single Loom skill export | Compatibility export | Legacy compatibility surface | Not a supported downstream install shape for the milestone #14 target. |
| Runtime carrier | Repository or external runtime | Runtime carrier policy | `.loom/bin` and `.loom/bootstrap` are unsupported legacy residue unless a migration issue explicitly classifies them. |

## Repository Adoption Modes

### Metadata-Only Adoption

Metadata-only adoption is a first-class repository mode. It records Loom
adoption truth in `.loom/installed-state.json`, preserves repo-owned governance
residue, and relies on a user/workstation skills provider.

Required semantics:

- `repo_payload.mode = "metadata-only"`.
- `runtime_provider = "global-cli"` or an equivalent provider declaration points
  to the global root `loom` CLI.
- `skills_provider.scope = "user"` or an equivalent layer declaration points to
  the user-level Codex Loom plugin.
- Absence of `.loom/bin` is intentional.
- Absence of `plugins/loom/.codex-plugin/plugin.json` is intentional.
- Absence of `plugins/loom/skills/` is intentional.
- Absence of `.agents/skills` and root `skills/` is intentional.
- Missing workstation provider registration is diagnosed as external
  workstation state, not as missing repository payload.

Metadata-only install, doctor, verify, host verify, and skills check must not
write or require `plugins/loom/skills/`, `.agents/skills`, or root `skills/`.
They may diagnose missing global CLI or workstation provider state, but those
diagnostics must remain outside repository truth unless installed-state
explicitly models the dependency.

### Legacy Embedded Repository Payload

Embedded payload mode is legacy residue for downstream repositories. It is a
detectable migration state, not a supported current install shape.

Required semantics:

- `repo_payload.mode = "embedded"` or equivalent legacy plugin-mode layers are
  migration inputs only.
- `plugins/loom/.codex-plugin/plugin.json` and `plugins/loom/skills/` are legacy
  repository payload artifacts.
- `loom host verify --host codex --mode plugin` is legacy verification and must
  not be presented as the current adoption path.
- Workstation registration remains separate and does not become repository
  truth.

Current Codex adoption installs the plugin at user scope from the global Loom
package and writes no repo-local plugin payload.

### Global CLI Provider Dependency

Repositories may explicitly depend on the global CLI runtime provider while
keeping repository adoption truth metadata-only or embedded:

- the repository may declare that `loom` command availability is required for
  migration, verification, or scenario execution;
- the provider version and executable provenance remain workstation/user-level
  state, not repository truth;
- `doctor`, `verify`, migration planning, and repair planning may diagnose the
  provider as missing, stale, incompatible, or unavailable;
- that diagnosis must not be rewritten as repository payload drift unless a
  repository-owned layer is also invalid.

This keeps the provider boundary clear: repository truth can depend on a global
provider without claiming to own or version the provider itself.

## Skills Granularity

Loom must keep these skills surfaces distinct:

| Surface | Granularity | Default? | Contract |
| --- | --- | --- | --- |
| User-level Codex Loom plugin | Full provider | Yes for metadata-only repositories | Provides Loom scenario skills from workstation state. |
| `plugins/loom/skills/` | Legacy embedded bundle | No | Unsupported legacy residue in downstream repositories. |
| `.agents/skills` | Compatibility export | No | Legacy compatibility residue unless a future host issue explicitly owns it. |
| Root `skills/` | Target-owned namespace | No | Protected as repo-owned unless explicit Loom ownership is proven. |
| Single generated skill package | One skill | No | Legacy distribution shape; the plugin payload is the only current skills publishing shape. |

Repair and upgrade plans must not delete or overwrite root `skills/`,
`.agents/skills`, or other repo-owned skills without explicit ownership proof
and an operator-approved mutating action.

## Runtime Carriers

Legacy `.loom/bin` and `.loom/bootstrap` carriers are unsupported residue in
downstream repositories, not skills providers and not plugin payload.
Installed-state and doctor output must classify them explicitly:

- `current`: the repository intentionally uses vendored runtime carriers.
- `retained-for-consumer-gate`: repo-native gates still depend on the carrier.
- `retained-for-audit`: kept as provenance while the active runtime is external
  or user-level.
- `obsolete`: no current installed-state or repo-native gate depends on it.
- `compatibility-only`: retained only so a repo-local wrapper or migration
  handshake can diagnose, compare, repair, or retire it without treating it as
  the active provider.

Metadata-only adoption must not create runtime carriers. Retained carriers are
migration residue only and must not make the repository look like an embedded
skills payload install.

## Runtime Provider Modes

Loom exposes one current user-facing runtime provider mode:

| Mode | Repository expectation | Provider authority | Validation entry |
| --- | --- | --- | --- |
| `global-cli` | `.loom/installed-state.json` records a dependency on the installed root `loom` command. No `.loom/bin` carrier is expected. | Global CLI runtime provider; workstation/user-level state remains outside repository truth. | `loom installed-state validate`, `loom doctor`, `loom verify`, `loom repair plan` |
| `repo-local-wrapper` | Legacy residue only for the milestone #14 target. | Migration/provenance classification, not active provider authority. | Diagnostics only |

For `global-cli` repositories, a detected `.loom/bin` directory is unsupported
legacy residue. It must not be used as proof that the repository owns the active
runtime provider.

Copyable validation commands for a `global-cli` repository:

```bash
loom installed-state validate --target . --json
loom detect --target . --json
loom doctor --target . --json
loom verify --target . --json
loom repair plan --target . --json
```

## Repo-Local Wrapper Compatibility

`repo-local-wrapper` is a compatibility carrier, not a third authority line.
Its job is to expose repo-local starter aliases and compatibility delegation
when a repository still carries vendored runtime entrypoints.

Contract:

- it may read repository-owned runtime carriers and route into the active Loom
  runtime/provider;
- it must not silently promote a detected `.loom/bin` runtime to the active
  provider just because the files exist;
- it must preserve fail-closed diagnostics when vendored runtime provenance,
  manifest alignment, or installed-state semantics drift;
- it is compatible with both vendored-runtime repositories and global
  CLI-provider repositories, but it does not override installed-state.

This lets migration stay diagnosable without making repo-local wrappers the
default truth source.

## Diagnosable Compatibility Mode

Compatibility mode is a diagnosable state, not a silent fallback. Loom uses the
term when repository truth, repo-local wrappers, legacy surfaces, or workstation
providers are intentionally being compared, migrated, or retired without yet
changing command behavior.

Compatibility mode may include:

- legacy `.loom/bin` or `.loom/bootstrap` retained as `compatibility-only`;
- a repo-local wrapper delegating to the global CLI runtime provider;
- workstation/user provider registration that is required but not yet proven;
- compatibility exports such as `.agents/skills`.

Compatibility mode must not:

- masquerade as a clean embedded payload install;
- upgrade legacy runtime residue into authoritative installed-state by
  detection alone;
- erase whether a failure belongs to repository truth, provider state, or
  workstation registration state.

## CLI Contract Implications

Mutating CLI commands must fail closed unless artifact type and scope are
explicit. The command surface must distinguish:

- workstation/user plugin registration;
- repository metadata-only adoption metadata;
- repository embedded plugin payload;
- full skills bundle compatibility export;
- single-skill compatibility export;
- runtime carrier install, retention, or retirement.

Read-only diagnostics may report all detected surfaces, but pass/fail semantics
must be based on the repository's declared adoption mode and the authority that
owns each artifact.

Migration, `doctor`, and `verify` therefore need a stable target-state rule:

- repository truth decides which layers are versioned and owned by the target
  repo;
- the global CLI runtime provider and workstation/user-level provider are
  external dependencies that may be required, diagnosed, or blocked, but they
  do not become repository truth;
- compatibility mode remains visible until residue, wrapper delegation, and
  provider gaps are either explicitly accepted or retired.
