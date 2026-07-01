# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: #1859
  - Child locators: #1860, #1861, #1862, #1863, #1864
  - Story Readiness: N/A; rationale: this is a bounded CLI governance workflow improvement, not a separate product story; consumer boundary: spec shaping, review, merge-ready, and release closeout may consume this as story intake non-applicability only; recheck condition: scope introduces multi-repo orchestration, automatic merge, product issue auto-close, or new governance semantics.
  - Story Business Confirmation: N/A; rationale: no business semantics are introduced; consumer boundary: spec shaping, review, merge-ready, and release closeout may consume this as business confirmation non-applicability only; recheck condition: scope changes user-facing product policy, security, data, release governance, or host authority behavior.
- Produces:
  - Scenario ids: S1, S2, S3, S4
  - Acceptance ids: A1, A2, A3, A4, A5
  - Behavior evidence expectation: runtime-upgrade contract checks, aggregate CLI contract checks, package/plugin payload hash checks, README/SKILL matrix review.
- Locator:
  - Spec locator: .loom/specs/WI-1859/spec.md
- Provenance:
  - Source issues: #1859/#1860/#1861/#1862/#1863/#1864
  - Freshness rule: revalidate after any runtime-upgrade CLI output, PR metadata flow, carrier closeout sync, generated skills, or docs matrix change.

## Goal

Make single-repository Loom runtime upgrades a safe, repeatable lane from workflow pin update through PR metadata readback and post-merge carrier-only closeout, without lowering existing governance gates.

## Scope

- In scope:
  - `loom runtime-upgrade pr` to render/create/update/read back the maintenance PR body.
  - `loom runtime-upgrade closeout --issue ... --sync --create-pr` to consume host issue/PR facts, write terminal carrier metadata, refresh recovery/status/shadow surfaces, and prepare the carrier-only closeout PR.
  - Contract coverage that closeout uses host-binding PR readback and preserves carrier-only review/head semantics.
  - Runtime-upgrade help, README, README.zh-CN, CLI matrix, and generated route matrix alignment.
- Out of scope:
  - Multi-repository batch mode.
  - Default automatic merge.
  - Default product issue closeout.
  - Hosted gate scheduler.
  - Large policy DSL or command rename.
  - Treating CI or PR body text as semantic approval.

## Key Scenarios

### Scenario S1

Given a repository with a Loom workflow version pin

When `loom runtime-upgrade prepare --to <version> --apply` runs

Then only the repository workflow pin and maintenance carrier artifacts are prepared.

### Scenario S2

Given a prepared runtime-upgrade branch

When `loom runtime-upgrade pr --create|--update` runs

Then Loom renders PR metadata, writes or updates the PR body, reads it back, and reports the next check command bound to the current branch/head.

### Scenario S3

Given the maintenance PR has merged and the maintenance issue is closed

When `loom runtime-upgrade closeout --issue <n> --sync --create-pr` runs

Then Loom reads host issue/PR terminal facts, writes terminal carrier metadata, refreshes closeout/merge-ready carrier surfaces, and prepares a carrier-only closeout PR without publishing, republishing, auto-merging, or closing unrelated product issues.

### Scenario S4

Given hosted checkout lacks the old reviewed head

When the closeout diff is carrier-only

Then Loom guidance and gate contracts keep the review/head fallback limited to carrier-only metadata drift and never treat CI or PR body metadata as semantic approval.

## Minimal Path Applicability

- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: v0.26.0 is a bounded CLI/docs contract change with targeted runtime-upgrade contract coverage; consumer boundary: suite validate, review, merge-ready, and closeout require minimal suite evidence and do not require full path research/contracts/readiness artifacts; recheck condition: scope expands into a scheduler, DSL, multi-repo orchestration, security, data, or host authority model change.

## Acceptance Criteria

- [ ] A1: Runtime-upgrade PR creation/update renders and reads back PR metadata before hosted gate.
- [ ] A2: Runtime-upgrade closeout can derive issue `closedAt`, PR merge commit, target branch, and hosted run URL from host readback.
- [ ] A3: Carrier-only closeout sync writes only repo carrier/recovery/shadow metadata and produces closeout PR next commands.
- [ ] A4: Carrier-only review guidance clearly says it does not approve product implementation.
- [ ] A5: README, README.zh-CN, CLI matrix, generated skill routes, contract checks, and package/plugin payload checks pass without lowering review, PR gate, hosted checks, release readback, or closeout evidence.
