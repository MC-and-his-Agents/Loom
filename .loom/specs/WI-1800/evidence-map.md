# WI-1800 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `src/skills/shared/scripts/fact_chain_support.py`; `src/skills/shared/scripts/loom_flow.py`; generated runtime copies | S1 S2 S6 | target/context and metadata carrier behavior | present | review / PR gate / merge wrapper / package smoke | Re-run target, merge-wrapper, controlled-merge, PR metadata, runtime parity, and package checks after resolver or metadata changes. |
| EV-002 | behavior_evidence | `src/skills/shared/scripts/governance_surface.py`; `src/skills/shared/scripts/loom_flow.py`; generated runtime copies | S3 S4 | strong detector, adversarial adoption evidence, repair-pr evidence | present | review / hosted gate / closeout | Re-run governance/adversarial/repair contract checks after gate or evidence schema changes. |
| EV-003 | behavior_evidence | `VERSION`; `package.json`; `plugins/loom/.codex-plugin/plugin.json`; `docs/evidence/v0.21.2-release-readiness.md` | S5 | v0.21.2 release candidate | present | release workflow / npm publish / plugin payload readback / #1802 | Re-run release surface, package, skills release-check, npm package smoke, and release readback checks after release metadata changes. |
| EV-004 | test_evidence | `test/target_resolution_test.py`; `test/checkpoint_canonicalization_test.py`; `test/retained_item_lookup_test.py`; `test/skills_surface_reference_integrity_test.py` | S2 | focused unit regressions | present | review / source loom_check | Re-run focused unit tests after resolver, checkpoint, retained lookup, or skills surface changes. |
| EV-005 | test_evidence | `tools/check_cli_contract.py`; `tools/check_npm_package.py`; `tools/check_release_surface.py`; `tools/loom_check.py` | S1 S3 S4 S5 S6 | contract, package, release, source validation | present | PR gate / hosted CI / controlled merge | Re-run contract surfaces, package/release checks, package smoke, and `loom_check --profile source .` after code, runtime, or metadata changes. |
| EV-006 | test_evidence | `examples/new-project/.loom/bootstrap/init-result.json`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift` | S1 S5 | demo bootstrap fixture parity | present | hosted loom-check / demo-bootstrap | Regenerate demo fixture and rerun fixture drift check after bootstrap/runtime changes. |
| EV-007 | fresh_verification_input | `.loom/progress/WI-1800.md` | EV-001-EV-006 / A1-A5 | PR #1816 / current head / validation summary | present | review / merge-ready / release closeout | Refresh after final validation, PR metadata readback, hosted checks, merge, release workflow, and #1802/#1800 closeout. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| v0.21.2 npm publish | deferred | Publish can only happen after PR #1816 merges to main and `loom-cli-release` runs. | #1802 release closeout | Read back tag, GitHub Release, npm package, workflow run, and installed/global CLI after merge. | #1802 |
| #1800 parent closeout | deferred | Parent closeout must wait for child PR merge and release evidence. | final parent closeout | Verify no open child blockers after #1802 is closed. | #1800 |
