# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1255.md`
- FR / parent locator: GitHub issue #1255
- Scope: Round 8 umbrella closeout for #1255 only; #1451, #1244/#1461/#1464/#1465, #1245/#1246/#1238, Round 9/11, Deferred roadmap, release/npm/live actions, shared contract/schema/parser/failure vocabulary changes, raw host merge, and any merge without separate watcher merge_lane grant are out of scope.
- Suite path: see `.loom/specs/WI-1255/spec.md`
- Current `HEAD`: bind to PR head before merge-ready consumption.
- PR locator: pending until PR creation.
- Host state locator: GitHub issue #1255 is OPEN/REOPENED before this closeout PR; #1260/#1261/#1262/#1263 and #1383/#1393-#1408 are terminal evidence inputs.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Umbrella issue | `https://github.com/MC-and-his-Agents/Loom/issues/1255` | open_before_closeout | GitHub host readback | Re-read before PR gate, merge_lane request, and post-merge closeout. |
| #1260 release/package parent | `.loom/progress/WI-1396.md`; GitHub issue #1260 | closed_out | repo carrier and GitHub host readback | Re-read #1260 host state and WI-1396 carrier before merge_lane request because `.loom/progress/WI-1260.md` is absent. |
| #1261 skills parent | `.loom/progress/WI-1261.md`; GitHub issue #1261 | closed_out | repo carrier and GitHub host readback | Re-read if parent carrier or host state changes before #1255 closeout merge. |
| #1262 demo bootstrap parent | `.loom/progress/WI-1262.md`; GitHub issue #1262 | closed_out | repo carrier and GitHub host readback | Re-read if parent carrier or host state changes before #1255 closeout merge. |
| #1263 runtime regression parent | `.loom/progress/WI-1263.md`; GitHub issue #1263 | closed_out | repo carrier and GitHub host readback | Re-read if parent carrier or host state changes before #1255 closeout merge. |
| Child evidence set | `.loom/progress/WI-1383.md`; `.loom/progress/WI-1393.md`; `.loom/progress/WI-1394.md`; `.loom/progress/WI-1395.md`; `.loom/progress/WI-1397.md`; `.loom/progress/WI-1398.md`; `.loom/progress/WI-1399.md`; `.loom/progress/WI-1400.md`; `.loom/progress/WI-1401.md`; `.loom/progress/WI-1402.md`; `.loom/progress/WI-1403.md`; `.loom/progress/WI-1404.md`; `.loom/progress/WI-1405.md`; `.loom/progress/WI-1406.md`; `.loom/progress/WI-1407.md`; `.loom/progress/WI-1408.md` | closed_out | repo carrier readback | Re-read if any child carrier or host state changes before #1255 closeout merge. |
| Aggregate validation evidence | `docs/evidence/validations/validation-release-validation-evidence-contract.md`; `docs/evidence/validations/validation-skills-surface-split-closeout.md`; `docs/evidence/validations/validation-runtime-regression-surface-closeout.md`; parent progress carriers | present | repo evidence and parent closeout carriers | Re-run only if closeout expands beyond carrier/evidence sync or changes validation tools, package/release behavior, fixture contents, generated runtime behavior, workflow semantics, or parser/gate contracts. |
| Suite path decision | `.loom/specs/WI-1255/spec.md` | N/A suite | authored Loom truth | Recheck if scope expands beyond umbrella closeout evidence/carriers. |
| Task carrier | `.loom/specs/WI-1255/task-carrier.md` | present | authored Loom truth | Bind to current head and PR before merge-ready consumption. |
| Review record | `.loom/reviews/WI-1255.json` | required before PR gate | authored review truth | Refresh if non-carrier inputs change after review. |
| Merge-ready basis | `.loom/shadow/merge-ready-loom.json`; PR gate output | required before merge_lane request | Loom gate output | Re-run after every PR head or PR metadata change. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `.loom/progress/WI-1255.md` | #1255 acceptance: release/package, skills, demo bootstrap, and runtime regression validation buckets are split into diagnosable surfaces while preserving aggregate validation coverage | WI-1255 / #1255 / #1260-#1263 terminal parent evidence / #1383/#1393-#1408 child evidence | present | review / merge-ready / PR gate / closeout | Refresh if parent/child terminal facts, surface names, aggregate command paths, release/no_release decision, or host states change. |
| EV-002 | test_evidence | `.loom/progress/WI-1255.md` | Parent terminal validation evidence and no_release facts from `.loom/progress/WI-1396.md`, `.loom/progress/WI-1261.md`, `.loom/progress/WI-1262.md`, and `.loom/progress/WI-1263.md`; #1260 evidence is consumed through WI-1396 because `.loom/progress/WI-1260.md` is absent | WI-1255 / parent carrier readback / current head / PR head | present | review / merge-ready / PR gate / closeout | Re-read parent carriers and host issues; rerun targeted aggregate checks only if the closeout changes validation tools, workflow/package/runtime behavior, or evidence contracts. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1255.md` | EV-001 and EV-002 plus current-head #1255 closeout validation, shadow parity, review readback, state-check, PR metadata, PR gate, and hosted checks recorded in `.loom/reviews/WI-1255.json` and validation output | WI-1255 / current head / PR head / reviewed head / validation summary | present | merge-ready / PR gate / closeout | Re-run validation, update recovery summary, refresh review, and rerun PR gate after every head or PR metadata change. |

## Release / No-Release Closeout

| Subject | Status | Rationale | Consumer boundary | Recheck condition |
| --- | --- | --- | --- | --- |
| #1255 release judgment | no_release | #1255 closeout records evidence and carrier metadata only. It does not publish packages, change VERSION, create tags, create GitHub Releases, publish npm artifacts, run release/npm/live deployment, or perform live external actions. #1260 release/package validation evidence is consumed through WI-1396 and host issue #1260 CLOSED/COMPLETED readback. | Satisfies the #1255 Release / No-Release Closeout Rule for this carrier-only umbrella closeout. | Recheck if scope adds package publication, release workflow execution, VERSION/tag changes, GitHub Release, npm publish, live action, or release-surface implementation changes. |

## Out Of Scope / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Formal minimal/full suite | N/A here | WI-1255 consumes completed Round 8 parent/child evidence and does not define new behavior or implementation phases. | Only skips formal suite artifacts; all evidence inventory, review, validation, PR gate, merge_lane, and closeout checks remain required. | Scope expands beyond #1255 carrier/evidence closeout or changes validation behavior, fixtures, generated runtime, workflows, release/package behavior, parser/gate contracts, permissions, or external-visible actions. | `.loom/specs/WI-1255/spec.md` |
| #1451 | out_of_scope | #1451 remains OPEN but is explicitly forbidden for this Round 8 scheduler closeout. | #1451 must not block or be closed by #1255 umbrella closeout. | Separate watcher grant changes #1451 scope. | GitHub issue #1451 |
| #1244/#1461/#1464/#1465 | out_of_scope | Watcher accepted #1244 final closeout before granting WI-1255 lanes; #1255 does not process #1244 artifacts. | No #1244 carrier, PR, issue, or lane work is authorized here. | Separate watcher grant changes scope. | GitHub issue #1244 |
