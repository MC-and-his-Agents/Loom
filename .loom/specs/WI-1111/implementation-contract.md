# WI-1111 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `docs/methodology/harness/cli-command-matrix.md`
- `.loom/work-items/WI-1111.md`
- `.loom/progress/WI-1111.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1111/spec.md`
- `.loom/specs/WI-1111/plan.md`
- `.loom/specs/WI-1111/implementation-contract.md`
- `.loom/reviews/WI-1111.spec.json`
- `.loom/reviews/WI-1111.json`

## Contract

- `loom help --json` declares `suite inspect` as the only implemented suite command for this Work Item.
- `loom suite inspect` remains routed to the existing read-only inspect implementation.
- The CLI contract check fails if `suite inspect` disappears from help JSON or loses its implemented suite-domain declaration.
- Planned suite scaffold, validate, analyze, evidence, consistency, and carrier commands remain out of the declared implemented surface.

## Non-Goals

- No `suite scaffold`.
- No `suite validate`.
- No evidence, consistency, or carrier suite subcommands.
- No readiness, review, merge-ready, closeout, Project, or host truth decisions.
