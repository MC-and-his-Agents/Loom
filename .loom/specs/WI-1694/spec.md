# WI-1694 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1694`
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1694 is a bounded README, skills, and fixture convergence change over already implemented `loom ship`, merge wrapper, and closeout policy surfaces. consumer boundary: suite validate, review, PR gate, controlled merge, closeout, and release #1696 may consume this minimal spec, plan, Work Item carriers, generated skills parity, and focused validation output. recheck condition: require full suite artifacts if scope expands into runtime `loom ship` behavior, new closeout policy semantics, release publishing, host mutation behavior, or a new skill surface.
- Consumes:
  - Work Item / FR locator: issue #1694 under FR #1693.
  - Story Readiness confirmed locator, blocking locator, or N/A rationale: N/A; #1694 is a bounded milestone #15 Work Item.
  - Story scenario locator, or N/A rationale: N/A; scenarios are authored below.
  - Story Business Confirmation confirmed locator, blocking locator, or N/A rationale: N/A; no business-domain semantics change.
- Produces:
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A5
  - Behavior evidence expectation: README, source skills, generated skills, plugin skills, and `ship-wrapper` contract agree that `loom ship` is the ordinary delivery path.
- Locator:
  - Spec locator: `.loom/specs/WI-1694/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1694
  - Freshness rule: Recheck after README, `src/skills`, generated skills, plugin skills, or `tools/check_cli_contract.py` changes.

## Goal

- Make Loom's ordinary delivery path understandable from README and skills surfaces.
- Preserve governance facts while avoiding a default user experience that requires manually chaining merge-ready, reconciliation, carrier closeout, and closeout checks.

## Scope

- In scope:
  - README / README.zh-CN daily delivery copy.
  - `src/skills` entry, route, merge-ready, and retire positioning.
  - Generated `skills/` and `plugins/loom/skills/` mirrors.
  - Targeted `ship-wrapper` fixture assertions for docs / skills drift.
- Out of scope:
  - Runtime behavior changes to `loom ship`, controlled merge, closeout, or release.
  - Release issue #1696 and milestone closeout.
  - New skill creation.

## Key Scenarios

### Scenario S1

Given a repository has installed Loom and a Work Item already has a PR

When a user or agent reads the README

Then they see `loom ship` as the ordinary delivery command and understand that light / standard changes do not need a second closeout PR by default.

### Scenario S2

Given an agent routes through Loom skills

When the task is ordinary PR delivery, merge-ready, or post-merge local cleanup

Then the skills surface positions `loom ship` as the normal delivery wrapper, `loom-merge-ready` as explicit preflight / diagnosis, and `loom-retire` as local cleanup after closeout evidence exists.

### Scenario S3

Given future changes modify README or skills delivery wording

When the `ship-wrapper` fixture group runs

Then it fails if docs / skills stop presenting `loom ship` as the primary ordinary delivery path or if generated skill mirrors drift from source.

## Behavior Evidence

- Story scenario mapping: N/A; scenarios S1-S3 are authored in this spec.
- Story readiness locator or N/A rationale: N/A; issue #1694 is already scoped and accepted as a milestone #15 Work Item.
- Story business confirmation locator or N/A rationale: N/A; no product-domain business semantics change.
- Scenario coverage:
  - S1 -> README / README.zh-CN diff and `ship-wrapper` fixture snippets.
  - S2 -> `src/skills` diff, generated mirrors, and `skills_surface.py check`.
  - S3 -> `tools/check_cli_contract.py --fixture-group ship-wrapper`.
- Expected evidence locator: `.loom/progress/WI-1694.md`
- Freshness rule: Refresh validation after changes to README, skills, generated mirrors, plugin mirrors, or fixture assertions.
- Execution ledger acceptance locator: `.loom/specs/WI-1694/plan.md`
- N/A rationale, if this is not a behavior-bearing change: N/A; README and skill routing are user-facing behavior surfaces.

## Exceptions And Boundaries

- Failure modes: README suggests the manual closeout chain as default, Chinese README adds avoidable English prose, generated skills drift from source, or fixture wording is too brittle.
- Operational boundaries: run all implementation in `/Users/mc/dev/Loom-WI-1694`; do not alter runtime closeout policy behavior.
- Rollback or fallback expectations: revert docs / skills / fixture copy for WI-1694 only; no runtime state migration is required.

## Acceptance Criteria

- [x] A1: README and README.zh-CN describe `loom ship` as the default day-to-day delivery path.
- [x] A2: README and skills explain that ordinary light / standard changes should not create a follow-up closeout PR by default.
- [x] A3: `src/skills` positions merge-ready as preflight / diagnosis and retire as local cleanup, not as the ordinary delivery chain.
- [x] A4: Generated `skills/` and `plugins/loom/skills/` mirrors are synchronized from `src/skills`.
- [x] A5: Targeted fixture checks guard the `loom ship` docs / skills entry contract.
