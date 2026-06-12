# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1261.md`
- FR / parent locator: GitHub issue #1261
- Scope: parent closeout for #1261 only; #1262, #1263, #1255, #1451, release/npm/live actions, and shared contract/schema/parser/failure vocabulary are out of scope.
- Suite path: see `.loom/specs/WI-1261/spec.md`
- Current `HEAD`: bind to PR head before merge-ready consumption.
- PR locator: pending until PR creation.
- Host state locator: GitHub issue #1261 is OPEN before this closeout PR; children #1397, #1398, #1399, and #1400 are CLOSED/COMPLETED.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Parent issue | `https://github.com/MC-and-his-Agents/Loom/issues/1261` | required | GitHub host readback | Re-read before PR gate and post-merge closeout. |
| Child #1397 | `.loom/progress/WI-1397.md`; PR #1419; PR #1420 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1398 | `.loom/progress/WI-1398.md`; PR #1424; PR #1429 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1399 | `.loom/progress/WI-1399.md`; PR #1432; PR #1441 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1400 | `.loom/progress/WI-1400.md`; PR #1443; PR #1450; `docs/evidence/validations/validation-skills-surface-split-closeout.md` | closed_out | repo carrier and GitHub host readback | Re-read if child carrier, evidence doc, or host state changes before parent closeout merge. |
| Suite path decision | `.loom/specs/WI-1261/spec.md` | N/A suite | authored Loom truth | Recheck if scope expands beyond parent closeout. |
| Task carrier | `.loom/specs/WI-1261/task-carrier.md` | present | authored Loom truth | Bind to current head and PR before merge-ready consumption. |
| Review record | `.loom/reviews/WI-1261.json` | required before PR gate | authored review truth | Refresh if non-review carrier inputs change after review. |
| Merge-ready basis | `.loom/shadow/merge-ready-loom.json`; PR gate output | required before merge_lane request | Loom gate output | Re-run after every PR head or PR metadata change. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `docs/evidence/validations/validation-skills-surface-split-closeout.md` | #1261 acceptance: named skills validation surfaces are documented and aggregate command contract is preserved | WI-1261 / #1261 / child #1397-#1400 terminal evidence | present | review / merge-ready / PR gate / closeout / later #1255 consumption | Refresh if surface names, failure names, aggregate command path, or child terminal facts change. |
| EV-002 | test_evidence | `.loom/progress/WI-1261.md` | Terminal validation evidence for docs sync, generated drift, package metadata, cache artifacts, launcher smoke, and aggregate skills check | WI-1261 / child carrier readback / PR head | present | review / merge-ready / PR gate / closeout / later #1255 consumption | Re-run targeted and aggregate skills checks if parent closeout changes validation surfaces or commands. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1261.md` | EV-001 and EV-002 plus current-head parent closeout validation | WI-1261 / current head / PR head / reviewed head | present | merge-ready / PR gate / closeout / later #1255 consumption | Re-run validation, update recovery summary, refresh review, and rerun PR gate after every head change. |

## Out Of Scope / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Formal minimal/full suite | N/A here | WI-1261 consumes completed child evidence and does not define new behavior or implementation phases. | Only skips formal suite artifacts; all validation, review, gate, and closeout checks remain required. | Scope expands beyond parent closeout carriers/evidence or changes skills command behavior. | `.loom/specs/WI-1261/spec.md` |
| #1255 umbrella closeout | N/A here | #1255 remains open/reopened and must consume all Round 8 parent evidence later under a separate grant. | WI-1261 may provide evidence for #1255 but does not close it. | Watcher grants #1255 closeout after #1261/#1262/#1263 terminalize. | GitHub issue #1255 |
| Release/npm/live action | N/A here | Parent closeout records evidence only and does not publish packages, create tags, create GitHub Releases, publish npm artifacts, or perform live actions. | No release evidence beyond no_release rationale is required for WI-1261. | Scope adds package publication, VERSION/tag changes, GitHub Release, npm publish, or live action. | N/A |
