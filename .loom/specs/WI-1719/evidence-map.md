# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1719.md`
- FR / parent locator: GitHub issue #1719
- Scope: Single SKILL version contract-only semantics in the legacy installer, plus WI-1719 carriers.
- Suite path: minimal
- Current `HEAD`: current checkout on branch `work/1719-skill-contract-version-only`; read back with `git rev-parse HEAD`.
- PR locator: not required; no PR requested for this build slice.
- Host state locator: GitHub issue #1719 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1719/spec.md` | required | suite scaffold plus authored WI-1719 spec | Recheck if #1719 scope or suite path changes. |
| `plan.md` | `.loom/specs/WI-1719/plan.md` | required | suite scaffold plus authored WI-1719 plan | Recheck if validation strategy or ownership changes. |
| suite path decision | `.loom/specs/WI-1719/spec.md` | minimal | authored WI-1719 suite decision | Recheck if scope expands beyond installer semantics and carriers. |
| execution breakdown / task carrier | `.loom/specs/WI-1719/task-carrier.md` | required | authored WI-1719 task carrier | Recheck issue, branch, worktree, and head before merge-ready. |
| review record | not required | not required | no PR/review requested | Required if PR or merge-ready is requested later. |
| merge-ready basis | not required | not required | no merge-ready requested | Required before merge-ready or merge. |
| host state | GitHub issue #1719 | required | `gh issue view 1719` readback | Recheck before PR creation, merge-ready, or closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `packages/loom-installer/src/index.ts` | `.loom/specs/WI-1719/spec.md` S1 S2 S3 | WI-1719 / contract-only single SKILL version semantics / current branch | present | build / review / merge-ready / closeout | Re-run installer tests after installer version-context, payload manifest, payload build, type, or compare-key changes. |
| EV-002 | test_evidence | `packages/loom-installer/test/installer.test.ts` | `.loom/specs/WI-1719/plan.md` validation strategy and A1-A4 | WI-1719 / regression tests / current branch | present | build / review / merge-ready / closeout | Re-run `npm --prefix packages/loom-installer test` after code, tests, or payload build changes. |
| EV-003 | docs_check_evidence | `packages/loom-installer/README.md` | `.loom/specs/WI-1719/plan.md` validation strategy | WI-1719 / installer docs sync / current branch | present | build / review / merge-ready | Re-run `npm --prefix packages/loom-installer run check:docs` after installer README changes. |
| EV-004 | build_evidence | `.loom/progress/WI-1719-build-evidence.json` | EV-001 EV-002 EV-003 | WI-1719 / build integration evidence | present | build / review / merge-ready | Refresh when implementation, validation, ownership, or forbidden-surface review changes. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1719.md` | EV-001 EV-002 EV-003 EV-004 plus fact-chain/suite checks | WI-1719 / latest validation summary / current branch | present | merge-ready / closeout / status | Refresh Latest Validation Summary after final validation, commit, push, or head changes. |

## Skipped / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| PR metadata / review record / merge-ready | not required | User requested commit and push only; no PR creation unless main thread asks. | PR gate / merge-ready / closeout | Required if a PR is opened or merge-ready is requested. | GitHub issue #1719 |
| High-cost guardian | not required | User explicitly said not to run high-cost guardian. | hosted review / merge-ready | Reconsider only on explicit main-thread request. | GitHub issue #1719 |
| Release / npm publish | not required | Forbidden by #1719 ownership. | release closeout | Recheck only in a separate release Work Item. | #1718 / release owner |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: not touched by WI-1719.
- Generated surface sync: installer payload generation is covered by `npm --prefix packages/loom-installer test`.
- Drift check requirement: rerun fact-chain, suite validate, suite evidence validate, suite carrier validate, and `git diff --check` after carrier or code changes.
