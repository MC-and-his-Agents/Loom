# Implementation Contract

## Work Item

- Item: `WI-561`
- Execution Entry: `.loom/work-items/WI-561.md`

## Approved Spec

- Spec Path: `.loom/specs/WI-561/spec.md`
- Spec Review Entry: `.loom/reviews/WI-561.spec.json`

## Implementation Scope

- In Scope: portable bootstrap output, active root Work Item binding, retirement of bootstrap placeholder from active execution.
- Out Of Scope: full execution attempt envelope implementation for child Work Items `#562` through `#565`.

## Validation Plan

- Automated Checks: `make loom-demo-new-project`, `python3 tools/skills_surface.py check`, `python3 tools/loom_status.py --target . --item WI-561`, `make check`.
- Manual Verification: repeated bootstrap run leaves only intentional tracked changes.

## Risks And Rollback

- Risks: root self-governance carriers can block review if spec/recovery/status drift.
- Rollback Boundary: reactivate `INIT-0001` only if `WI-561` fact-chain activation becomes unreadable.

## Host Binding

- Pull Request: to be created from `work/531-v080-baseline-repair`.
- Reviewed Head: current branch head after validation.
