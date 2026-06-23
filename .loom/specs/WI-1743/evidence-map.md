# WI-1743 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/v0.20.0-release-readiness.md | S3 release readiness | WI-1743 / release evidence | present | review / PR gate / release closeout | Refresh when release target, scope, validation, publish boundary, or post-merge closeout contract changes. |
| EV-002 | behavior_evidence | VERSION, package.json | S1 version authority | v0.20.0 / 0.20.0 | present | release workflow / npm package check | Keep root VERSION and package.json aligned. |
| EV-003 | behavior_evidence | plugins/loom/.codex-plugin/plugin.json | S2 plugin payload metadata | v0.20.0 payload candidate | present | package check / host plugin readback | Recompute payload hash and rerun package checks after payload metadata or files change. |
| EV-004 | behavior_evidence | README.md; tools/check_cli_contract.py | S3 ship main-path behavior | v0.20.0 ship main path | present | review / release closeout | Re-run ship-wrapper regression after ship contract, closeout policy, or README path changes. |
| EV-005 | test_evidence | tools/version_surface_check.py; tools/check_npm_package.py; tools/check_release_surface.py | A1 A2 A4 | WI-1743 validation | present | review / hosted checks / release workflow | Re-run after package, workflow, version, or release evidence changes. |
| EV-006 | test_evidence | npm run test:package; npm pack --dry-run --json --ignore-scripts | A4 package smoke | root npm package | present | review / release workflow | Re-run after package payload changes. |
| EV-007 | test_evidence | tools/check_cli_contract.py --fixture-group ship-wrapper | A4 ship regression | ship-wrapper fixture group | present | review / release closeout | Re-run after ship-wrapper or ship path changes. |
| EV-008 | fresh_verification_input | .loom/progress/WI-1743.md | EV-001-EV-007 / A4 gate evidence | current branch / current head | present | review / merge-ready / closeout | Refresh after validation and before review. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| post-merge release readback | deferred | Final tag, GitHub Release, npm, and plugin payload readback can only exist after the release PR merges and `loom-cli-release` runs. | final closeout | Fill after release PR merges and publish workflow completes. | #1743 |
