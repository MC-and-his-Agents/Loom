# Loom Skills

Loom skills are executable agent scenarios over the 30-command public CLI.
They orchestrate host capabilities; they are not governance truth or extra CLI
commands.

## Start

Use `loom-init` as the root interaction entrypoint. Repository adoption is
metadata-only:

```bash
loom install --target . --apply --json
loom installed-state validate --target . --json
loom verify --target . --json
loom doctor --target . --json
```

Install or update the Codex plugin through the Codex marketplace or plugin
host. That workstation action is separate from repository adoption.

## Scenario set

- `loom-init`: detect, diagnose, and route.
- `loom-adopt`: metadata-only install and verification.
- `loom-resume`: derive context from explicit Work Item, branch, worktree, PR,
  and GitHub readback.
- `loom-story`: shape story readiness before execution.
- `loom-build`: admit a typed Work Item and branch before a PR exists.
- `loom-pre-review`: bind a real PR/current head before review.
- `loom-spec-review` and `loom-review`: semantic review consumed through host
  attestation.
- `loom-merge-ready`: current-head attestation, hosted gate, checks, and
  mergeability.
- `loom-handoff`: produce a session summary without repository mutation.
- `loom-retire`: retire the local issue-scoped worktree.

See [route-matrix.md](./route-matrix.md) for exact public commands.

## Product boundary

Ordinary execution produces zero repo current, status, progress, review,
shadow, or closeout carrier mutations. Retired commands cannot be restored by
profiles. Review and closeout truth are host attestations; product acceptance
belongs to the product owner and is only consumed by Loom through an
authenticated locator.

`src/skills/` is canonical. Distribution builds generate `skills/`, plugin,
example, and package surfaces and verify their digests.
