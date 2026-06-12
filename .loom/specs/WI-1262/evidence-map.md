# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1262.md`
- FR / parent locator: GitHub issue #1262
- Scope: parent closeout for #1262 only; #1263, #1255, #1451, release/npm/live actions, and shared contract/schema/parser/failure vocabulary are out of scope.
- Suite path: see `.loom/specs/WI-1262/spec.md`
- Current `HEAD`: bind to PR head before merge-ready consumption.
- PR locator: pending until PR creation.
- Host state locator: GitHub issue #1262 is OPEN before this closeout PR; children #1401, #1402, #1403, and #1404 are CLOSED/COMPLETED.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Parent issue | `https://github.com/MC-and-his-Agents/Loom/issues/1262` | required | GitHub host readback | Re-read before PR gate and post-merge closeout. |
| Child #1401 | `.loom/progress/WI-1401.md`; PR #1417; PR #1421 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1402 | `.loom/progress/WI-1402.md`; PR #1431 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1403 | `.loom/progress/WI-1403.md`; PR #1425 | closed_out | repo carrier and GitHub host readback | Re-read if child carrier or host state changes before parent closeout merge. |
| Child #1404 | `.loom/progress/WI-1404.md`; PR #1446; parent closeout evidence map | closed_out | repo carrier and GitHub host readback | Re-read if child carrier, parent evidence map, or host state changes before parent closeout merge. |
| Suite path decision | `.loom/specs/WI-1262/spec.md` | N/A suite | authored Loom truth | Recheck if scope expands beyond parent closeout. |
| Task carrier | `.loom/specs/WI-1262/task-carrier.md` | present | authored Loom truth | Bind to current head and PR before merge-ready consumption. |
| Review record | `.loom/reviews/WI-1262.json` | required before PR gate | authored review truth | Refresh if non-review carrier inputs change after review. |
| Merge-ready basis | `.loom/shadow/merge-ready-loom.json`; PR gate output | required before merge_lane request | Loom gate output | Re-run after every PR head or PR metadata change. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `.loom/progress/WI-1404.md` | #1262 acceptance: named demo bootstrap validation surfaces are documented in #1404 parent evidence and `docs/methodology/harness/repo-local-gate-starter.md`, and aggregate command contract is preserved | WI-1262 / #1262 / child #1401-#1404 terminal evidence | present | review / merge-ready / PR gate / closeout / later #1255 consumption | Refresh if surface names, failure names, aggregate command path, or child terminal facts change. |
| EV-002 | test_evidence | `.loom/progress/WI-1262.md` | Terminal validation evidence for generation, canonicalization, fixture drift, examples cleanliness, and aggregate demo bootstrap fixture check | WI-1262 / child carrier readback / PR head | present | review / merge-ready / PR gate / closeout / later #1255 consumption | Re-run targeted and aggregate demo bootstrap checks if parent closeout changes validation surfaces or commands. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1262.md` | EV-001 and EV-002 plus current-head parent closeout validation | WI-1262 / current head / PR head / reviewed head | present | merge-ready / PR gate / closeout / later #1255 consumption | Re-run validation, update recovery summary, refresh review, and rerun PR gate after every head change. |

## Out Of Scope / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Formal minimal/full suite | N/A here | WI-1262 consumes completed child evidence and does not define new behavior or implementation phases. | Only skips formal suite artifacts; all validation, review, gate, and closeout checks remain required. | Scope expands beyond parent closeout carriers/evidence or changes demo bootstrap command behavior. | `.loom/specs/WI-1262/spec.md` |
| #1263 runtime parent closeout | N/A here | #1263 remains open and must be processed under a separate watcher grant. | WI-1262 may coexist with #1263 evidence but does not close it. | Watcher grants #1263 closeout after runtime children terminalize. | GitHub issue #1263 |
| #1255 umbrella closeout | N/A here | #1255 remains open/reopened and must consume all Round 8 parent evidence later under a separate grant. | WI-1262 may provide evidence for #1255 but does not close it. | Watcher grants #1255 closeout after #1262/#1263 terminalize and any remaining Round 8 parent evidence is ready. | GitHub issue #1255 |
| Release/npm/live action | N/A here | Parent closeout records evidence only and does not publish packages, create tags, create GitHub Releases, publish npm artifacts, or perform live actions. | No release evidence beyond no_release rationale is required for WI-1262. | Scope adds package publication, VERSION/tag changes, GitHub Release, npm publish, or live action. | N/A |
