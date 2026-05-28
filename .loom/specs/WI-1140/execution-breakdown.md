# WI-1140 Execution Breakdown

| Unit | Scope | Files | Validation | Status |
| --- | --- | --- | --- | --- |
| unit-1140-1 | Shared runtime consumes suite CLI JSON for build and fails closed without CLI JSON. | `src/skills/shared/scripts/loom_flow.py`, `skills/shared/scripts/loom_flow.py`, `.loom/bin/loom_flow.py` | py compile; CLI contract; build JSON smoke | in_progress |
| unit-1140-2 | Skill/docs contracts state CLI JSON consumption boundaries. | `src/skills/*/SKILL.md`, `src/skills/route-matrix.md`, `skills/*`, `docs/methodology/harness/full-spec-suite-cli-surface.md`, `docs/methodology/harness/cli-command-matrix.md` | skills surface check; focused rg | in_progress |
| unit-1140-3 | Loom carriers, evidence, review, merge-ready, and closeout evidence. | `.loom/work-items/WI-1140.md`, `.loom/progress/WI-1140.md`, `.loom/specs/WI-1140/*`, `.loom/reviews/WI-1140*` | suite/evidence/carrier validators; gate chain | in_progress |
