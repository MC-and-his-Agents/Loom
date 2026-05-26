# WI-1040 Spec

## Goal

Clarify the replacement boundary for `tasks.md`, GitHub issue/sub-issue, Project item, checklist, external tracker, and `not_applicable` task carriers in the #1017 execution breakdown contract.

## Scope

- Define `tasks.md` as an optional task carrier, not a core required Loom artifact.
- Define GitHub issue/sub-issue, Project item, checklist, and external tracker as task carriers or host views that cannot replace `Work Item` truth.
- Preserve behavior evidence, test evidence, review, merge-ready, and closeout as separate truth/evidence surfaces.
- Record #1020 follow-up needs without changing skills routing or generated runtime surface.

## Non-Goals

- Do not redefine task carrier core types beyond #1038.
- Do not implement GitHub Project automation.
- Do not define evidence-map or consistency-analysis.
- Do not change gate-chain, CLI, skills routing, scenario `SKILL.md`, or generated skills runtime surface.

## Scenarios

### Scenario 1: `tasks.md` Is Optional

Given a Loom project wants local task tracking,
When it uses `tasks.md` for execution breakdown units,
Then `tasks.md` is treated as `repo_tasks_md` carrier and not as a required core artifact.

### Scenario 2: Host Done Is Not Evidence

Given a task carrier reports `done`, Project `Done`, checklist checked, issue closed, or external tracker `Done`,
When review, merge-ready, or closeout consumes the result,
Then that host state cannot replace behavior evidence, test evidence, review pass, merge-ready pass, or closeout.

### Scenario 3: Work Item Truth Is Protected

Given a carrier conflicts with `Work Item`, recovery, review, merge checkpoint, or closeout truth,
When a Loom consumer reads the carrier,
Then it must treat the conflict as stale, drift, or a blocking consistency gap and return to the truth carrier.

## Evidence Mapping

- Behavior evidence: contract text in `docs/methodology/harness/task-carrier-contract.md` and `docs/adoption/github-profile.md`.
- Test evidence: focused `rg`, `python3 tools/skills_surface.py check`, and `python3 tools/loom_check.py --profile source --source-surface contract-only .`.
- Story business confirmation: `not_applicable`; this is a methodology contract change.

## Acceptance Criteria

- [x] `tasks.md` is defined as a carrier, not a core required artifact.
- [x] GitHub issue/project/checklist/external tracker carriers cannot replace `Work Item`.
- [x] task done / Project Done / checklist checked cannot replace behavior evidence or test evidence.
- [x] review, merge-ready, and closeout truth remain separate.
- [x] #1020 follow-up needs are recorded without modifying skills/generated surfaces.
