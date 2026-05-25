# CLI-First Legacy Migration Playbook

This playbook defines the #897 migration path for repositories that already
contain Loom-era runtime, companion, skills, or installer residue but do not yet
publish `loom-installed-state/v2`.

The goal is not to mutate adopted repositories from Loom core. The CLI-first
phase freezes the read, diagnosis, repair-plan, upgrade-plan, and verify
semantics so each repository can consume the plan through its own authority
model.

## Command Sequence

| Step | Command | Required behavior |
| --- | --- | --- |
| 1 | `loom detect --target <repo> --json` | Read installed surfaces and classify `uninstalled`, `legacy`, `mixed-legacy`, `mixed`, or `current`. |
| 2 | `loom doctor --target <repo> --json` | Fail closed for missing/invalid installed-state or legacy surfaces and fall back to `loom repair plan`. |
| 3 | `loom repair plan --target <repo> --json` | Emit a non-mutating plan that separates installed-state repair from legacy surface classification. |
| 4 | `loom upgrade-plan --target <repo> --json` | Emit a non-mutating delivery plan. Legacy or missing metadata keeps upgrade apply blocked. |
| 5 | `loom verify --target <repo> --json` | Pass only when `doctor` passes. Legacy or mixed surfaces remain blocking. |

`loom repair apply`, `loom install --apply`, `loom upgrade --apply`, and rollback
continue to require separate write ownership and rollback evidence. They are not
approved by #897.

## Repository Patterns

| Repository | Current class | Migration reading |
| --- | --- | --- |
| WebEnvoy | `mixed-legacy` | Deep-existing attach repo with repo-local runtime, bootstrap residue, repo companion, and repo-local skills. Repo-native guardian, live evidence, and controlled merge remain WebEnvoy-owned. |
| Syvert | `mixed-legacy` | Strong-governance repo with vendored runtime compatibility, bootstrap residue, and repo companion. Shadow evidence and guardian residue remain repo-owned until a later authority migration. |
| HotCP | `mixed-legacy` | Full-bootstrap repo with repo-local runtime, bootstrap residue, repo companion, repo-local skills, hooks, and advisory local gates. Local hooks must not be described as GitHub server-enforced Loom gates. |

## Release Boundary

#897 does not publish a Loom root release or npm package by itself. It supplies
the legacy validation evidence consumed by #996.

The #897 release judgment is therefore:

- `no-publish-for-897`: no package or tag is required only for this validation
  batch.
- `publish-decision-owned-by-996`: #996 must consume this evidence with version
  surface checks, release readiness checks, tag/npm state, and final publish or
  no-publish judgment.
- `legacy-repos-not-upgraded`: WebEnvoy, Syvert, and HotCP remain blocked by
  missing `loom-installed-state/v2` and legacy surfaces until repo-owned repair
  and upgrade work explicitly applies changes.
