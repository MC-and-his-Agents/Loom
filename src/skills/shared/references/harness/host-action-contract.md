# Host Action Contract

Loom consumes host facts and invokes host mutations only through public commands.
It does not mirror host truth into repository execution carriers.

## Ownership

| Fact or action | Owner | Loom behavior |
| --- | --- | --- |
| issue/FR/WI tree | GitHub | read back; mutate only for an explicit route/close action |
| PR, branch, head, checks, merge | GitHub | read back immediately before gate or mutation |
| semantic review | GitHub attestation/artifact | verify current head, run, and artifact digest |
| `external_result_sources` | external provider | read the retained result and evidence locator; never execute the provider action |
| worktree | local Git | create/check/retire only the explicit issue-scoped worktree |
| plugin install/cache | Codex | report a typed provider action; do not mutate from Loom |

Every failure exposes one primary cause. `remediation_command` must be a public
Loom command. Human, GitHub, npm, Git, or Codex work is represented separately
as `manual_action` or `provider_action`.

Host mutations require explicit `--apply`, fresh authenticated readback, and
post-mutation readback. Local fixture files are never valid mutation authority.
External result readback consumes declared results only; it does not execute host actions or turn provider output into Loom-owned truth.

See [host-lifecycle-boundary.md](./host-lifecycle-boundary.md) and
[closeout-gate.md](./closeout-gate.md).
