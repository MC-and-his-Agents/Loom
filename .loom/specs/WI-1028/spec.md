# WI-1028 Spec

## Goal

Skills routing must recognize delivery planning and issue-tree planning requests before it sends the operator into build, review, merge-ready, or story-only shaping.

## Acceptance

- `skills/route-matrix.md` and source truth define delivery planning / issue-tree plan as a `loom-init` routing result.
- `loom-init` explains when to output planning instead of routing to build, review, merge-ready, or spec review.
- `loom-story` explains that story shaping does not output issue-tree plans; oversized stories or requested execution trees return to `loom-init` planning.
- README surfaces state that planning does not replace `Work Item`, spec, review, merge-ready, or closeout truth.
- Generated skills runtime copies are synchronized.

## Non-goals

- Do not redefine the delivery planning contract from #1024.
- Do not edit the issue-tree-plan template from #1025.
- Do not edit PR slicing strategy from #1026.
- Do not edit GitHub mapping from #1027.
- Do not implement CLI commands or GitHub API automation.
