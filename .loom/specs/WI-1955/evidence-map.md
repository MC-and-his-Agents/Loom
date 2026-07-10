# WI-1955 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | docs/evidence/v0.27.1-release-readiness.md | S2 / A2 | WI-1955 / release evidence | present | review / PR gate / release closeout | Refresh when release scope, validation, publish boundary, or post-merge closeout contract changes. |
| EV-002 | behavior_evidence | VERSION; package.json | S1 / A1 | v0.27.1 / 0.27.1 | present | release workflow / npm package check | Keep root VERSION and package.json aligned. |
| EV-003 | behavior_evidence | plugins/loom/.codex-plugin/plugin.json | S1 / A1 | v0.27.1 plugin payload candidate | present | package check / host plugin readback | Recompute payload hash and rerun package checks after payload metadata or files change. |
| EV-004 | test_evidence | tools/version_surface_check.py; tools/check_npm_package.py; tools/check_release_surface.py | A1 A2 A3 | WI-1955 validation | present | review / hosted checks / release workflow | Rerun after package, workflow, version, or release evidence changes. |
| EV-005 | test_evidence | npm pack --dry-run --json --ignore-scripts | A3 | root npm package | present | review / release workflow | Rerun after package payload changes. |
| EV-006 | fresh_verification_input | .loom/progress/WI-1955.md | EV-001-EV-005 / A3 | current branch / current head | present | review / merge-ready / closeout | Refresh after validation and before review. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| post-merge release readback | deferred | Final tag, GitHub Release, npm, and workflow readback can only exist after the release PR merges and the main-push workflow completes. | final closeout | Fill after release PR merges and publish workflow completes. | #1955 |
| issue/Phase/milestone closeout | deferred | #1928, #1930, #1955, #1954, and milestone #26 must not close until release readback and carrier terminalization pass. | final closeout | Close only after release readback and carrier closeout-sync pass. | #1928 / #1930 / #1955 / #1954 / milestone #26 |
