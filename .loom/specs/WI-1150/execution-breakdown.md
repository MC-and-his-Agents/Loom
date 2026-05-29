# WI-1150 Execution Breakdown

| Unit | Scope | Owner | Status | Validation |
| --- | --- | --- | --- | --- |
| unit-1150-1 | Add stale evidence negative fixture and assertions. | worker | in_progress | `suite evidence validate` blocks stale evidence with taxonomy/remediation. |
| unit-1150-2 | Add host conflict negative fixture and assertions. | worker | in_progress | `suite carrier validate` blocks host conflicts with taxonomy/remediation. |
| unit-1150-3 | Sync generated runtime surface and record Work Item evidence. | worker | in_progress | `tools/skills_surface.py check` and contract-only `loom_check` pass. |
