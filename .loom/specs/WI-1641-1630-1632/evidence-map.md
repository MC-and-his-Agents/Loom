# Evidence Map

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `.loom/specs/WI-1641-1630-1632/spec.md` | AC-1 AC-2 AC-3 AC-4 AC-5 | WI-1641-1630-1632 / plugin payload behavior | present | review / merge-ready / closeout | Refresh after changing skills generation or package surface. |
| EV-002 | test_evidence | `python3 tools/skills_surface.py check` | AC-1 AC-2 AC-3 | WI-1641-1630-1632 / generated skills parity | present | review / merge-ready / closeout | Rerun after any `src/skills`, `skills`, or `plugins/loom/skills` change. |
| EV-003 | test_evidence | `python3 tools/check_npm_package.py`; `python3 tools/version_surface_check.py` | AC-1 AC-3 AC-5 | WI-1641-1630-1632 / package and version surface | present | review / merge-ready / closeout | Rerun after package manifest or version authority changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1641-1630-1632.md` | EV-001 EV-002 EV-003 | WI-1641-1630-1632 / current head | present | review / merge-ready / closeout | Refresh before PR body/gate consumption. |
