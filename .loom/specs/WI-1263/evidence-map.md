# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1263.md`
- FR / parent locator: GitHub issue #1263
- Scope: parent closeout for #1263 only; #1255, #1451, release/npm/live actions, and shared contract/schema/parser/failure vocabulary are out of scope.
- Suite path: see `.loom/specs/WI-1263/spec.md`
- Current `HEAD`: bind to PR head before merge-ready consumption.
- PR locator: pending until PR creation.
- Host state locator: GitHub issue #1263 is OPEN before this closeout PR; children #1405, #1406, #1407, and #1408 are CLOSED/COMPLETED.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Parent issue | `https://github.com/MC-and-his-Agents/Loom/issues/1263` | required | GitHub host readback | Re-read before PR gate and post-merge closeout. |
| Child #1405 | `.loom/progress/WI-1405.md`; PR #1418 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1406 | `.loom/progress/WI-1406.md`; PR #1433; PR #1447 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1407 | `.loom/progress/WI-1407.md`; PR #1444 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1408 | `.loom/progress/WI-1408.md`; PR #1455; parent closeout evidence map | closed_out | repo carrier and GitHub host readback | Re-read if child carrier, parent evidence map, or host state changes before parent closeout merge. |
| Runtime aggregate evidence | `docs/evidence/validations/validation-runtime-regression-surface-closeout.md`; `make loom-check-runtime-regression` | present | repo evidence and command contract | Re-run if closeout expands beyond parent carrier evidence or runtime checker/Makefile semantics change. |
| Suite path decision | `.loom/specs/WI-1263/spec.md` | N/A suite | authored Loom truth | Recheck if scope expands beyond parent closeout. |
| Task carrier | `.loom/specs/WI-1263/task-carrier.md` | present | authored Loom truth | Bind to current head and PR before merge-ready consumption. |
| Review record | `.loom/reviews/WI-1263.json` | required before PR gate | authored review truth | Refresh if non-review carrier inputs change after review. |
| Merge-ready basis | `.loom/shadow/merge-ready-loom.json`; PR gate output | required before merge_lane request | Loom gate output | Re-run after every PR head or PR metadata change. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `.loom/progress/WI-1408.md` | #1263 acceptance: named runtime regression validation surfaces are documented in #1408 parent evidence and `docs/evidence/validations/validation-runtime-regression-surface-closeout.md`, and aggregate command contract is preserved | WI-1263 / #1263 / child #1405-#1408 terminal evidence | present | review / merge-ready / PR gate / closeout / later #1255 consumption | Refresh if surface names, failure names, aggregate command path, or child terminal facts change. |
| EV-002 | test_evidence | `.loom/progress/WI-1263.md` | Terminal validation evidence for locking, subprocess-env purity, tempdir cleanup, demo fixture cleanliness, and aggregate runtime regression check | WI-1263 / child carrier readback / PR head | present | review / merge-ready / PR gate / closeout / later #1255 consumption | Re-run targeted and aggregate runtime regression checks if parent closeout changes validation surfaces or commands. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1263.md` | EV-001 and EV-002 plus current-head parent closeout validation | WI-1263 / current head / PR head / reviewed head | present | merge-ready / PR gate / closeout / later #1255 consumption | Re-run validation, update recovery summary, refresh review, and rerun PR gate after every head change. |

## Out Of Scope / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Formal minimal/full suite | N/A here | WI-1263 consumes completed child evidence and does not define new behavior or implementation phases. | Only skips formal suite artifacts; all validation, review, gate, and closeout checks remain required. | Scope expands beyond parent closeout carriers/evidence or changes runtime regression command behavior. | `.loom/specs/WI-1263/spec.md` |
| #1255 umbrella closeout | N/A here | #1255 remains open/reopened and must consume all Round 8 parent evidence later under a separate grant. | WI-1263 may provide evidence for #1255 but does not close it. | Watcher grants #1255 closeout after all Round 8 parent evidence is terminalized and release/no_release evidence is ready. | GitHub issue #1255 |
| Release/npm/live action | N/A here | Parent closeout records evidence only and does not publish packages, create tags, create GitHub Releases, publish npm artifacts, or perform live actions. | No release evidence beyond no_release rationale is required for WI-1263. | Scope adds package publication, VERSION/tag changes, GitHub Release, npm publish, or live action. | N/A |
