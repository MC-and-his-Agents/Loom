# Repo / Global Artifact Classification

This contract freezes the #1898 boundary for moving Loom workstation-only
artifacts out of adopted repositories without weakening repository truth.

It answers one question: when an artifact exists under `.loom/`, which authority
owns it, and may a future implementation move it to `~/.loom/`?

## Authority Rule

Repository truth stays versioned in the target repository. Workstation
acceleration, recovery convenience, diagnostics cache, and long runtime output
belong in the user's global Loom state.

Moving an artifact to `~/.loom/` must never make global state a source of
review, merge-ready, closeout, issue, PR, or release truth. Global state may
speed discovery and resume, but every gate still consumes repository truth,
host mirrors, or retained evidence with current bindings.

## Classification Matrix

| Class | Default location | Authority | Examples | May move to `~/.loom/`? |
| --- | --- | --- | --- | --- |
| Repository adoption truth | Repository | Target repository | `.loom/installed-state.json`, repo companion declarations, repo interop metadata | No |
| Work Item truth | Repository | Target repository | `.loom/work-items/**`, `.loom/progress/**`, `.loom/status/current.md` | No |
| Review and gate truth | Repository | Target repository | `.loom/reviews/**`, authored spec review, merge-ready basis, closeout terminal metadata | No |
| Spec suite and task carriers | Repository | Target repository | `.loom/specs/**`, evidence map, task carrier, implementation contract | No |
| Host mirror / retained host evidence | Repository or host locator | Host control plane plus repository locator | PR/issue/project/check readback locators, release/no-release evidence, closeout sync evidence | No, except long raw payload copies |
| Runtime execution cache | Global workstation cache | Workstation | command stdout/stderr captures, transient run JSON, tool temp files | Yes |
| Long diagnostics artifacts | Global workstation cache | Workstation | full doctor payloads, large hosted check logs, replay transcripts | Yes, with repository locator/hash |
| Batch planning cache | Global workstation cache | Workstation | `~/.loom/repositories.json`, freshness cache, per-repo upgrade classification cache | Yes |
| Recoverability index | Global workstation cache | Workstation | per-repo last seen item id, last local command summary, artifact locator index | Yes, as an accelerator only |

## Repo Carrier Shape After Slimdown

When a runtime or diagnostic artifact moves global, the repository carrier may
store only the small facts needed to audit the relationship:

- producing command
- subject Work Item or repository locator
- head SHA or merge commit when applicable
- short result summary
- artifact hash
- global artifact locator
- freshness rule

The repository carrier must not embed long logs, raw runtime payloads, plugin
payloads, Codex cache contents, or workstation registry state.

## Global Path Contract

Global per-repository artifacts should be addressed under a stable repository
id:

```text
~/.loom/repos/<repo-id>/
```

The `<repo-id>` must be derived from a stable workstation registry entry or an
equivalent path/remote hash. A repo id is workstation-local; it is not a
repository truth key and must not be committed as an authoritative identity.

Suggested global subpaths:

| Subpath | Purpose |
| --- | --- |
| `runtime/` | transient command outputs and tool run payloads |
| `tmp/` | scratch files that are safe to regenerate |
| `checks/` | local and hosted diagnostic readbacks too large for repo carriers |
| `artifacts/` | hash-addressed retained payload copies referenced by repo summaries |
| `index.json` | workstation-local locator index and freshness metadata |

## Consumer Boundary

Consumers may read global artifacts only as evidence payloads behind a
repository-owned locator. They must fail closed when the repository summary,
hash, head binding, or freshness rule does not match the global artifact.

Consumers must not:

- treat global cache presence as proof that a repository is adopted;
- treat global cache presence as review approval, merge-ready, or closeout;
- mutate a repository because a workstation cache says it is safe;
- require global cache to exist when repository truth and host readback are
  otherwise sufficient;
- copy global runtime, plugin, or skills payload back into the repository.

## Migration Rule

Legacy repository-local runtime/tmp/check artifacts are migration inputs. A
migration may shadow-copy or move ignored cache paths to the global store, then
write only repository summaries and locators when a versioned carrier needs
them.

Tracked repository truth must not be deleted by cache migration. Tracked legacy
residue must be classified separately by the legacy migration Work Items before
removal.

## Validation Requirements

Implementation slices that consume this contract must prove:

- repository truth still validates without global cache;
- resume / doctor / review / merge-ready / closeout do not depend on
  repo-local runtime cache;
- global cache mismatches fail closed to repository-local validation;
- repository carriers contain summaries and locators, not long payloads;
- workstation registry entries accelerate planning but do not replace
  per-repository adoption validation.
