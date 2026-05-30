# Plan

## Suite Contract

- Suite path consumed: full
- Spec locator: .loom/specs/WI-1153/spec.md
- Plan locator: .loom/specs/WI-1153/plan.md
- Story Readiness consumed state: #1153 issue body
- Story Business Confirmation consumed state: not required because this is governance regression behavior.
- Freshness rule: refresh .loom/progress/WI-1153.md after final validation and before PR handoff.

## Phases

### Phase 1

- Objective: Add non-mutating host fixture inputs for closeout and reconciliation.
- Deliverable: issue, PR, and Project payload fixture flags in shared `loom_flow.py`.
- Exit condition: closeout/reconciliation checks can run without live host mutation for fixture payloads.

### Phase 2

- Objective: Add an end-to-end governance chain fixture.
- Deliverable: CLI contract fixture creates a local git repo with Work Item, review, merge-ready attempt, PR, issue, Project, required checks, and merge commit evidence.
- Exit condition: pass fixture succeeds only with the full chain present.

### Phase 3

- Objective: Add PR-merged-alone negative coverage and synchronize generated surfaces.
- Deliverable: fixture blocks when PR is merged but issue/Project closeout evidence is missing; runtime copies are synchronized.
- Exit condition: `check_cli_contract.py`, skills surface check, and source contract loom_check pass.

## Validation

- Scenario mapping:
  - S1 -> automated validation evidence: closeout/reconciliation fixture pass case.
  - S2 -> automated validation evidence: closeout/reconciliation fixture negative case.
  - S3 -> automated validation evidence: PR gate command and PR body metadata in PR #pending.
- Acceptance mapping:
  - A1 -> test evidence: `python3 tools/check_cli_contract.py`.
  - A2 -> behavior evidence: `skills/shared/scripts/loom_flow.py`.
  - A3 -> test evidence: `python3 tools/skills_surface.py check`.
  - A4 -> structural check: WI-1153 work item, progress, evidence map, task carrier, and review records.
