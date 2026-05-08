# WI-706 Implementation Contract

## Write Scope

- `.loom/work-items/WI-706.md`
- `.loom/progress/WI-706.md`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/specs/WI-706/`
- `docs/methodology/harness/`
- `src/skills/`
- `skills/`

## Constraints

- Subagent output is evidence until main execution integrates it into existing Loom carriers.
- Delegation must declare read scope and write ownership before execution.
- Overlapping ownership must block or require explicit local integration.
- Repeated blockers must recommend root-cause escalation instead of silent retry loops.
- Build readiness cannot silently mutate review or merge-ready records.
