# WI-1713 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1713.md`
- FR / parent locator: issue #1711, direct Work Item issue #1713
- Scope: plugin payload release metadata and hash validation.
- Suite path: minimal
- Current `HEAD`: refresh after final commit.
- PR locator, or N/A rationale: N/A until PR is created.
- Host state locator, or N/A rationale: GitHub issue #1713

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1713/spec.md` | required | authored for issue #1713 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1713/plan.md` | required | authored for issue #1713 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1713/spec.md` | minimal | authored suite contract | Recheck before review or PR gate. |
| execution breakdown / task carrier | `.loom/specs/WI-1713/task-carrier.md` | required | authored task carrier | Recheck before review or closeout. |
| build evidence | `.loom/progress/WI-1713-build-evidence.json` | required | authored during build | Refresh after validation. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `plugins/loom/.codex-plugin/plugin.json` | S1 release metadata fields | WI-1713 / branch `work/1713-plugin-release-metadata` | present | build / review / PR gate | Recompute payload hash and rerun package/version checks after plugin metadata changes. |
| EV-002 | behavior_evidence | `tools/check_npm_package.py` | S1-S3 metadata validation and readback with `tools/version_surface_check.py` and `tools/loom.py` | WI-1713 / package and version surfaces | present | build / review / hosted release and node-installer gates | Re-run py_compile, package check, version surface check, and `loom version --json` after checker changes. |
| EV-003 | test_evidence | `test/plugin_payload_hash_test.py` | S2 hash self-reference and deterministic behavior | WI-1713 / hash tests | present | build / review / package gate | Re-run hash tests after hash algorithm changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1713.md` | EV-001 EV-002 EV-003 | current branch / current head before push | present | build / review / push evidence | Refresh after validation and commit. |
| EV-005 | build_evidence | `.loom/progress/WI-1713-build-evidence.json` | integrated implementation and validation evidence | WI-1713 / build checkpoint | present | build / review / PR gate | Regenerate through loom-build after validation or ownership changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| source/cache/runtime freshness comparison | out_of_scope | Owned by #1721. | planning only | If CLI starts comparing Codex plugin layers. | #1721 |
| stale plugin refresh guidance | out_of_scope | Owned by #1716 after freshness reporting lands. | planning only | If CLI emits refresh actions. | #1716 |
| exact release commit SHA readback | out_of_scope | A committed file cannot contain the SHA of the same commit; release closeout owns final tag/npm/GitHub readback. | release closeout | When v0.19.0 release is prepared. | #1718 |
