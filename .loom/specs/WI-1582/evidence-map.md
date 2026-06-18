# WI-1582 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1582/spec.md` S1 S2 S3 | closeout hosted admission surface and review/carrier binding behavior | present | review, PR gate, hosted admission, closeout carrier PRs | Re-run targeted terminal closeout fixture after runtime changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | `.loom/specs/WI-1582/spec.md` A1 A2 A3 A4 | terminal closeout hosted fixture and merge-ready regression fixture | present | local validation and hosted checks | Extend fixture if freeze snapshot, carrier refresh, or PR metadata fields change. |
| EV-003 | parity_evidence | `tools/skills_surface.py check --surface generated-tree-drift` | `.loom/specs/WI-1582/spec.md` A5 | generated runtime copy parity | present | generated skills runtime consumers | Regenerate skills surface after shared runtime changes. |
| EV-004 | runtime_fixture_evidence | `make loom-demo-new-project-check` | `.loom/specs/WI-1582/spec.md` A5 | demo bootstrap runtime fixture parity | present | demo/bootstrap consumers | Re-sync demo bootstrap after runtime changes. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1582.md` | EV-001; EV-002; EV-003; EV-004 | current branch validation summary | present | review, PR gate, hosted checks, milestone closeout | Re-run validation after code, fixture, runtime copy, PR metadata, or review changes. |
