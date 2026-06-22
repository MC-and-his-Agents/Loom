# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1722.md`
- FR / parent locator: GitHub issue #1722
- Scope: Legacy installer single-skill fail-closed semantics, plus WI-1722 carriers.
- Suite path: minimal
- Current `HEAD`: current checkout on branch `work/1722-retire-single-skill-installer`; read back with `git rev-parse HEAD`.
- PR locator: pending.
- Host state locator: GitHub issue #1722 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1722/spec.md` | required | authored WI-1722 spec | Recheck if #1722 scope or suite path changes. |
| `plan.md` | `.loom/specs/WI-1722/plan.md` | required | authored WI-1722 plan | Recheck if validation strategy or ownership changes. |
| suite path decision | `.loom/specs/WI-1722/spec.md` | minimal | authored WI-1722 suite decision | Recheck if scope expands beyond installer semantics and carriers. |
| execution breakdown / task carrier | `.loom/specs/WI-1722/task-carrier.md` | required | authored WI-1722 task carrier | Recheck issue, branch, worktree, and head before merge-ready. |
| review record | `.loom/reviews/WI-1722.json` | pending | main control later | Required before merge-ready or merge. |
| merge-ready basis | pending | pending | main control later | Required before merge-ready or merge. |
| host state | GitHub issue #1722 | required | `gh issue view 1722` readback | Recheck before PR creation, merge-ready, or closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `packages/loom-installer/src/index.ts` | `.loom/specs/WI-1722/spec.md` S1 S2 | WI-1722 / skill-mode fail-closed diagnostics / current branch | present | build / review / merge-ready / closeout | Re-run installer tests after skill-mode, status diagnostic, or version-context changes. |
| EV-002 | behavior_evidence | `packages/loom-installer/src/codex.ts` | `.loom/specs/WI-1722/spec.md` S3 and `packages/loom-installer/src/claude.ts` companion behavior | WI-1722 / direct export fail-closed behavior / current branch | present | build / review / merge-ready / closeout | Re-run installer tests after host-specific direct function changes. |
| EV-003 | test_evidence | `packages/loom-installer/test/installer.test.ts` | `.loom/specs/WI-1722/plan.md` validation strategy and A1-A5 | WI-1722 / regression tests / current branch | present | build / review / merge-ready / closeout | Re-run `npm --prefix packages/loom-installer test` after code, tests, or payload build changes. |
| EV-004 | docs_check_evidence | `packages/loom-installer/README.md` | `.loom/specs/WI-1722/plan.md` validation strategy plus package README.zh-CN/package.json companion copy | WI-1722 / installer package docs sync / current branch | present | build / review / merge-ready | Re-run `npm --prefix packages/loom-installer run check:docs` after installer README changes. |
| EV-005 | build_evidence | `.loom/progress/WI-1722-build-evidence.json` | EV-001 EV-002 EV-003 EV-004 | WI-1722 / build integration evidence | present | build / review / merge-ready | Refresh when implementation, validation, ownership, or forbidden-surface review changes. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1722.md` | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1722 / latest validation summary / current branch | present | merge-ready / closeout / status | Refresh Latest Validation Summary after final validation, commit, push, or head changes. |

## Skipped / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Shared status/bootstrap carriers | skipped | Parallel controller lanes own shared truth carriers; this worker owns WI-1722-specific carriers only. | main control / merge-ready | Main control may sync shared carriers after integrating parallel lanes. | GitHub issue #1722 |
| High-cost guardian | skipped | Bounded installer worker lane; not requested by controller. | hosted review / merge-ready | Reconsider only on explicit main-control request. | GitHub issue #1722 |
| Release / npm publish | forbidden | #1722 explicitly forbids version bump, publish, and release actions. | release closeout | Separate release Work Item only. | release owner |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: not touched by WI-1722.
- Generated surface sync: installer payload generation is covered by `npm --prefix packages/loom-installer test`.
- Drift check requirement: rerun fact-chain, suite validate, suite evidence validate, suite carrier validate, and `git diff --check` after carrier or code changes.
