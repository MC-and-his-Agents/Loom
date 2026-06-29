# WI-1790 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/runtime_wrapper.py`; `tools/loom_init.py`; `tools/loom_flow.py`; `tools/loom_check.py`; `tools/loom_status.py` | S1 S2 | WI-1790 / wrapper runtime resolution | present | review / package smoke / installed CLI | Re-run py compile, package smoke, and installed CLI smoke after wrapper changes. |
| EV-002 | behavior_evidence | `skills/shared/scripts/loom_init.py`; `src/skills/shared/scripts/loom_init.py`; `plugins/loom/skills/shared/scripts/loom_init.py` | S3 | bootstrap output contract | present | review / CLI wrapper / demo fixture | Re-run generated/runtime parity and demo fixture checks after bootstrap runtime changes. |
| EV-003 | test_evidence | `test/npm-package-smoke.test.mjs`; `tools/check_npm_package.py` | S1 S4 | packed npm package payload | present | PR gate / release workflow / installed smoke | Re-run `npm run test:package` and `python3 tools/check_npm_package.py` after package payload changes. |
| EV-004 | behavior_evidence | `VERSION`; `package.json`; `plugins/loom/.codex-plugin/plugin.json` | S5 | v0.21.1 release candidate | present | release workflow / npm publish / plugin refresh | Re-run version surface, release surface, package check, and plugin payload metadata check after release metadata changes. |
| EV-005 | test_evidence | `examples/new-project/.loom/bootstrap/init-result.json`; `python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift` | S2 S3 | demo bootstrap fixture parity | present | hosted loom-check / demo-bootstrap | Regenerate demo fixture and rerun fixture drift check after runtime changes. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1790.md` | EV-001-EV-005 / A5 | PR #1790 / current head / validation summary | present | review / merge-ready / closeout | Refresh after validation, PR metadata readback, hosted checks, publish, and plugin payload refresh. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| v0.21.1 npm publish | deferred | Publish can only happen after PR #1790 merges to main and the release workflow runs. | final closeout | Read back tag, GitHub Release, npm package, and workflow run after merge. | PR #1790 |
| Codex plugin payload refresh | deferred | User-level plugin payload should be refreshed after the fixed package is published. | final closeout | Re-run host install/register/doctor after npm publish. | PR #1790 |
