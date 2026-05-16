# Implementation Contract

## Work Item

- Item: WI-763
- Execution Entry: self-governance/pr-semantic-review-gate/763

## Approved Spec

- Spec Path: .loom/specs/WI-763/spec.md
- Spec Review Entry: .loom/reviews/WI-763.spec.json

## Implementation Scope

- In Scope:
  - PR merge gate command and workflow.
  - Controlled merge check/merge command.
  - PR #762 regression evidence and docs.
  - Generated skills and installed-runtime fixtures.
  - Live host enforcement proof and controlled merge closeout.
- Out Of Scope:
  - Default review engine switching.
  - Replacing GitHub branch protection or rulesets.
  - Treating raw review output as approval truth.

## Validation Plan

- Automated Checks:
  - `python3 -m py_compile` for touched Python entrypoints.
  - `python3 tools/loom_check.py .`.
  - `make skills-check`.
  - `git diff --check`.
- Manual Verification:
  - branch protection/ruleset readback requires `loom-pr-merge-gate`.
  - PR check run readback shows `loom-pr-merge-gate` passed for the PR head.
  - controlled merge dry-run confirms required checks and authored review boundary.

## Risks And Rollback

- Risks:
  - host required-check configuration can block all PRs if the workflow name or trigger drifts.
  - stale authored review records must fail closed even when CI is green.
  - local developer machines may expose shimmed toolchains; checks must avoid HOME-dependent shims inside isolated test homes.
- Rollback Boundary:
  - remove the required `loom-pr-merge-gate` host enforcement before reverting the workflow or command.

## Host Binding

- Pull Request: to be assigned after branch publication.
- Reviewed Head: a5b3a0c3b978f60e52056bdf0a4c3ec909954894
