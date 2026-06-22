# WI-1720 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1720.md`
- FR / parent locator: issue #1711 sequence, direct Work Item issue #1720
- Scope: target install/upgrade versus host plugin refresh command boundary.
- Suite path: minimal
- Current `HEAD`: refresh after commit.
- PR locator, or N/A rationale: N/A; user explicitly requested no PR unless later requested.
- Host state locator, or N/A rationale: GitHub issue #1720

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1720/spec.md` | required | authored for issue #1720 | Recheck when scope changes. |
| `plan.md` | `.loom/specs/WI-1720/plan.md` | required | authored for issue #1720 | Recheck when validation changes. |
| suite path decision | `.loom/specs/WI-1720/spec.md` | minimal | authored suite contract | Recheck before review or PR gate. |
| execution breakdown / task carrier | `.loom/specs/WI-1720/task-carrier.md` | required | authored task carrier | Recheck before review or closeout. |
| build evidence | `.loom/progress/WI-1720-build-evidence.json` | required | authored during build | Refresh after validation. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | S1-S3 CLI output boundary | WI-1720 / branch `work/1720-host-command-boundary-v2` | present | build / review / PR gate | Re-run py_compile and targeted CLI contract after CLI output changes. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | A1-A4 fixture/doc guard | WI-1720 / adoption-host-metadata surface | present | build / review / PR gate | Re-run `tools/check_cli_contract.py --surface adoption-host-metadata`. |
| EV-003 | behavior_evidence | `README.md` | A4 docs sync with README.zh-CN and src/skills/README.md guarded by `tools/check_cli_contract.py` | WI-1720 / docs boundary snippets | present | docs sync / review | Re-read docs and rerun targeted contract check after wording changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1720.md` | EV-001 EV-002 EV-003 | current branch / current head before push | present | build / review / push evidence | Refresh after validation and commit. |
| EV-005 | build_evidence | `.loom/progress/WI-1720-build-evidence.json` | integrated implementation and validation evidence | WI-1720 / build checkpoint | present | build / review / PR gate | Regenerate through loom-build after validation or ownership changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| payload hash semantics | out_of_scope | Owned by #1714 and later hash implementation work. | planning only | If CLI starts comparing payload hashes. | #1714 |
| plugin freshness report | out_of_scope | Owned by #1715. | planning only | If CLI emits source/cache/readback freshness report. | #1715 |
| release/version/npm publish | out_of_scope | #1720 only changes CLI/docs/checker boundary wording. | release/no-release judgment | If VERSION, tags, npm, release workflow, or `packages/loom-installer/**` changes. | release owner |
