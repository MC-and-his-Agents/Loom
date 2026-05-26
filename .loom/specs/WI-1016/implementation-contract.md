# WI-1016 Implementation Contract

## Work Item

- Work Item: WI-1016.
- Execution entry: issue #1016 -> branch work/1016-spec-suite -> worktree /Users/mc/dev/Loom-1016-spec-suite.

## Approved Spec

- Spec path: .loom/specs/WI-1016/spec.md.
- Plan path: .loom/specs/WI-1016/plan.md.

## Implementation Scope

- Covered: docs/methodology/templates/spec-suite.md, docs scaffold templates, README listing, WI-1016 carrier, and #1028 terminal carrier sync required to clear stale active workspace conflict.
- Not covered: source/generated skills sync, route matrix, scenario SKILL.md, task carrier, evidence-map, consistency-analysis, gate-chain, CLI.

## Validation Plan

- git diff --check.
- focused rg checks for suite contract and mapping terms.
- python3 tools/skills_surface.py check.
- python3 tools/loom_check.py --profile source --source-surface contract-only .
- PR #1086 checks.

## Risks And Rollback

- Risk: generated / skills references remain intentionally stale until #1020.
- Mitigation: #1020 handoff comment and #1036 deferred handoff comment record the required sync.
- Rollback: revert PR #1086.

## Host Binding

- PR: #1086.
- Branch: work/1016-spec-suite.
- Review record: .loom/reviews/WI-1016.json.
