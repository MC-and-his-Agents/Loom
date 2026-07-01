# WI-1869 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or `not_applicable` rationale: full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1869 is a bounded closeout recovery polish slice with concrete dogfood regressions and direct CLI contract coverage; consumer boundary: suite validate, review, PR gate, merge-ready, closeout, and release follow-up may consume the minimal suite without treating skipped full-path artifacts as completed; recheck condition: require full suite artifacts if this expands into a new gate scheduler, a broad closeout command redesign, or release automation semantics.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1869
  - Child issue locators: #1870, #1871, #1872, #1873
  - Story Readiness consumed state: non-applicable; the issue tree and v0.26.0 dogfood failures define the accepted product problem.
  - Story Business Confirmation consumed state: non-applicable; this is an internal Loom operator experience polish release.
- Produces:
  - Scenario ids / locators: S1 stale native dependency sync, S2 release readback closeout-head guidance, S3 terminal closeout carrier-only review, S4 closeout common path guidance.
  - Acceptance ids / locators: A1-A6 below.
  - Behavior evidence expectation: contract tests and docs/help matrix updates.
- Locator:
  - Spec locator: `.loom/specs/WI-1869/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: #1869-#1873 and milestone #24.
  - Freshness rule: rerun targeted CLI contracts after changes to reconciliation, release readback, review binding, closeout docs/help, PR metadata, or plugin payload files.

## Goal

Reduce repeated closeout recovery rework without lowering governance gates.

## Scope

- In scope:
  - Execute planned `remove_blocked_by` reconciliation sync actions through GitHub native dependency mutations.
  - Suggest the published release commit when release readback is run from a later closeout carrier head.
  - Allow `review record --surface closeout` in terminal `closed_out` state for carrier-only review evidence that does not approve product behavior.
  - Let hosted freeze/admission consume that closeout carrier-only review on closeout surfaces.
  - Put `loom closeout run ... --apply` and release closeout-head guidance into README,中文 README, CLI matrix, and help routing.
- Out of scope:
  - New gate scheduling system.
  - Broad closeout command redesign.
  - Multi-repo batching.
  - Lowering semantic review, PR metadata, hosted gate, release readback, or closeout evidence requirements.
  - v0.26.1 version bump and publish; #1874 owns release.

## Key Scenarios

### Scenario S1

Given reconciliation audit plans stale native dependency removal

When `reconciliation sync --apply` runs

Then Loom executes `removeBlockedBy` and records applied action evidence instead of requiring manual GraphQL.

### Scenario S2

Given release artifacts are bound to the release PR merge commit

When release readback is run from a later closeout carrier head

Then Loom keeps the verdict fail-closed but suggests rerunning readback with `--commit <release-merge-commit>`.

### Scenario S3

Given a Work Item is terminal `closed_out`

When a closeout carrier-only PR needs current-head review evidence

Then `review record --surface closeout` may write carrier-only review metadata and hosted closeout admission consumes it without semantic implementation approval.

### Scenario S4

Given a post-merge closeout is ready to sync

When the operator looks at help or README

Then the common path points to `loom closeout run ... --apply` and gives exact recovery guidance.

## Acceptance Criteria

- [x] A1: reconciliation sync apply executes `remove_blocked_by`.
- [x] A2: release readback closeout-head drift fixture suggests the release commit.
- [x] A3: terminal `closed_out` closeout review writes `carrier_only_closeout_review`, not `semantic_review_disposition`.
- [x] A4: hosted closeout admission consumes carrier-only closeout review without product approval.
- [x] A5: README, README.zh-CN, CLI matrix, and help expose the common closeout path.
- [x] A6: targeted and aggregate local CLI contracts pass.
