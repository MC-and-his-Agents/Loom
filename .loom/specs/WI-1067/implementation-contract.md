# WI-1067 Implementation Contract

## Required Behavior

- New user-facing install text names the root `loom` CLI as the only primary install entry.
- Host plugin and SKILLS payloads are described as managed by `loom host ...` and `loom skills ...`.
- README-level and Codex install docs do not show `loom-installer` commands as runnable current install examples.
- Historical installer references remain tied to deprecated evidence and non-advancement checks.
- Static doc-sync needles must match the new documentation facts and must not require obsolete clone/symlink/installer primary-path wording.

## Validation Focus

- Search for remaining primary-path `loom-installer`, full-repo clone, direct symlink, standalone plugin, and standalone SKILLS install wording.
- Run package, release-surface, version-surface, CLI-contract, installer legacy checks, Loom fact-chain/adopt/shadow gates, and `make check`.
