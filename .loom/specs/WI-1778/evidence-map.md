# WI-1778 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/v0.21.0-release-readiness.md | S3 release readiness | WI-1778 / release evidence | present | review / PR gate / release closeout | Refresh when release target, scope, validation, publish boundary, or post-merge closeout contract changes. |
| EV-002 | behavior_evidence | VERSION, package.json | S1 version authority | v0.21.0 / 0.21.0 | present | release workflow / npm package check | Keep root VERSION and package.json aligned. |
| EV-003 | behavior_evidence | plugins/loom/.codex-plugin/plugin.json | S2 plugin payload metadata | v0.21.0 payload candidate | present | package check / host plugin readback | Recompute payload hash and rerun package checks after payload metadata or files change. |
| EV-004 | behavior_evidence | tools/loom.py; tools/check_cli_contract.py; docs/evidence/fixtures/release-readback-fixtures.json | S3 closeout readback behavior | v0.21.0 release readback path | present | review / release closeout | Re-run release-readback and ship-wrapper regressions after readback, closeout sync, or ship preflight changes. |
| EV-005 | test_evidence | tools/version_surface_check.py; tools/check_npm_package.py; tools/check_release_surface.py | A1 A2 A4 | WI-1778 validation | present | review / hosted checks / release workflow | Re-run after package, workflow, version, or release evidence changes. |
| EV-006 | test_evidence | npm run test:package; npm pack --dry-run --json --ignore-scripts | A4 package smoke | root npm package | present | review / release workflow | Re-run after package payload changes. |
| EV-007 | test_evidence | tools/check_cli_contract.py --surface release-readback; tools/check_cli_contract.py --fixture-group ship-wrapper | A4 closeout/readback regression | release-readback and ship-wrapper fixture groups | present | review / release closeout | Re-run after release readback, ship status, closeout sync, or ship-wrapper paths change. |
| EV-008 | fresh_verification_input | .loom/progress/WI-1778.md | EV-001-EV-007 / A4 gate evidence | current branch / current head | present | review / merge-ready / closeout | Refresh after validation and before review. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| post-merge release readback | deferred | Final tag, GitHub Release, npm, and plugin payload readback can only exist after the release PR merges and `loom-cli-release` runs. | final closeout | Fill after release PR merges and publish workflow completes. | #1778 |
