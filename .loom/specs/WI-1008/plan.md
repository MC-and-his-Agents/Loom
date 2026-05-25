# WI-1008 Plan

1. Update `loom-cli-release` so `push` events on `main` can publish eligible CLI releases while pull requests remain judgment-only.
2. Split CLI publish behavior from release-control-only changes so #1008 does not trigger the first release.
3. Make existing `v*` tags on different commits a blocking release state instead of a non-blocking judgment.
4. Update release-surface documentation and checker needles for main auto-publish, dispatch repair, and tag-collision fail-closed semantics.
5. Validate release surface, version surface, CLI contract, workflow YAML syntax, installer release checks, and Loom carrier checks.
6. Open the issue-scoped PR for #1008 and consume PR/merge evidence before closing the issue.
