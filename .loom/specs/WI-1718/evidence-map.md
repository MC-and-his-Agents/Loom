# WI-1718 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/v0.19.0-release-readiness.md | S4 release readiness | WI-1718 / release evidence | present | review / PR gate / release closeout | Refresh when release target, scope, validation, publish boundary, or post-merge closeout contract changes. |
| EV-002 | behavior_evidence | VERSION, package.json | S1 version authority | v0.19.0 / 0.19.0 | present | release workflow / npm package check | Keep root VERSION and package.json aligned. |
| EV-003 | behavior_evidence | plugins/loom/.codex-plugin/plugin.json | S2 plugin payload metadata | v0.19.0 payload candidate | present | package check / host plugin readback | Recompute payload hash and rerun package checks after payload metadata or files change. |
| EV-004 | behavior_evidence | tools/stamp_plugin_payload_metadata.py; .github/workflows/loom-cli-release.yml | S3 publish-time source SHA stamping | npm publish workflow | present | release workflow / npm package readback | Re-run release workflow contract and stamp script checks after workflow or script changes. |
| EV-005 | test_evidence | tools/version_surface_check.py; tools/check_npm_package.py; tools/check_release_surface.py | A1 A2 A3 A5 | WI-1718 validation | present | review / hosted checks / release workflow | Re-run after package, workflow, version, or release evidence changes. |
| EV-006 | test_evidence | npm run test:package; npm pack --dry-run --json --ignore-scripts | A5 package smoke | root npm package | present | review / release workflow | Re-run after package payload changes. |
| EV-007 | fresh_verification_input | .loom/progress/WI-1718.md | EV-001-EV-006 / A5 gate evidence | current branch / current head | present | review / merge-ready / closeout | Refresh after validation and before review. |
## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| post-merge release readback | deferred | Final tag, GitHub Release, npm, and plugin payload readback can only exist after the release PR merges and `loom-cli-release` runs. | final closeout | Fill after release PR merges and publish workflow completes. | #1718 |
| npm deprecate legacy installer | separate_confirmation_required | `npm deprecate @mc-and-his-agents/loom-installer` is an external registry write and must not be bundled into automatic v0.19.0 publish. | release closeout | Ask for explicit confirmation before execution. | #1732 / #1718 |
