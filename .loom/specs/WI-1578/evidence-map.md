# WI-1578 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1578/spec.md` S1 S2 S3 | PR metadata effective surface behavior | present | review, PR gate, closeout carrier PRs | Re-run focused pr-metadata checks after metadata surface changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1578/spec.md` A1 | closeout render/preflight fixture coverage | present | local validation and hosted checks | Extend the focused fixture if PR metadata fields or surface mapping changes. |
| EV-003 | parity_evidence | `tools/skills_surface.py check --surface generated-tree-drift` | `.loom/specs/WI-1578/spec.md` A2 | generated runtime copy parity | present | generated skills runtime consumers | Regenerate skills surface after shared runtime changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1578.md` | EV-001; EV-002; EV-003 | current branch validation summary | present | review, PR gate, hosted checks, milestone closeout | Re-run validation after code, fixture, runtime copy, PR metadata, or review changes. |
