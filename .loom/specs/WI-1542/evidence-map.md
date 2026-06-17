# WI-1542 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | implementation | `src/skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1542/spec.md` S1 S2 S3 | WI-1542 retained lookup ranking | current | repo-local runtime and generated skills runtime copies | Re-run py_compile and retained lookup tests after lookup changes. |
| EV-002 | regression | `test/retained_item_lookup_test.py` | `.loom/specs/WI-1542/spec.md` S1 S2 S3 | retained lookup ambiguity handling | current | local and CI checks | Add fixtures if new retained evidence types are introduced. |
| EV-003 | generated_surface | `skills/**/.loom-runtime/shared/scripts/loom_flow.py`; `skills/shared/scripts/loom_flow.py` | `.loom/specs/WI-1542/plan.md` step 5 | source-to-runtime parity | current | executable skill distribution | Re-run `python3 tools/skills_surface.py generate` and surface checks. |
| EV-004 | live_closeout_readback | `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py closeout check --target . --issue 1544 --pr 1548 --branch work/1544-lane-orchestration-protocol --gate-profile closeout-contract` | `.loom/specs/WI-1542/spec.md` S1 | issue #1544 retained lookup no longer ambiguous | current | #1543/#1515 closeout readback | Re-run if issue #1544, PR #1548, or retained Work Item carriers change. |
