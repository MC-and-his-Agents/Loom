# WI-1696 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/v0.18.0-release-readiness.md | S2 release readiness | WI-1696 / release evidence | present | review / PR gate / release closeout | Refresh when release target, scope, validation, or publish boundary changes. |
| EV-002 | behavior_evidence | VERSION, package.json | S1 version authority | v0.18.0 / 0.18.0 | present | release workflow / npm package check | Keep root VERSION and package.json aligned. |
| EV-003 | test_evidence | tools/version_surface_check.py; tools/check_npm_package.py; tools/check_release_surface.py | A1 A3 | WI-1696 validation | present | review / hosted checks / release workflow | Re-run after package or release evidence changes. |
| EV-004 | test_evidence | npm run test:package; npm pack --dry-run --json --ignore-scripts | A3 package smoke | root npm package | present | review / release workflow | Re-run after package payload changes. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1696.md | EV-001 EV-002 EV-003 EV-004 / A4 gate evidence | current branch / current head | present | review / merge-ready / closeout | Refresh after validation and before review. |
