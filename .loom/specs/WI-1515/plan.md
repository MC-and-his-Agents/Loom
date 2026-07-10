# WI-1515 Plan

## Suite Contract

- Suite path: not_applicable
- Suite path consumed: not_applicable
- Spec locator: .loom/specs/WI-1515/spec.md
- Plan locator: .loom/specs/WI-1515/plan.md
- Formal-suite not_applicable: rationale: WI-1515 is the milestone/12 release-required closeout lane and does not define new product behavior, runtime semantics, gate schema, or implementation acceptance scenarios. consumer boundary: build, review, PR metadata, hosted checks, release readback, closeout reconciliation, shadow freshness, and #1505/#1515 terminal carrier sync consume this plan plus release evidence; the formal spec-suite artifacts remain skipped. recheck condition: require a minimal or full suite if #1515 expands into new CLI/runtime behavior, gate behavior, schema changes, fixture semantics, generated skill payload changes beyond version metadata, or external-visible release mechanics.

## Steps

1. Record the milestone/12 release-required judgment and v0.14.2 version authority surfaces.
2. Validate release surfaces locally: version authority, release workflow contract, npm package manifest, package tests, npm dry-run payload, CLI version output, skills release check, skills surface, CLI contract, suite, fact-chain, work-item audit, and diff hygiene.
3. Record build evidence and current-head implementation review for the release PR diff.
4. Render and preflight the PR body from Loom metadata before creating or updating the #1515 release PR.
5. Open the release PR and consume hosted checks without merging while publication remains unapproved.
6. After explicit user approval, merge the release PR through the host merge path and read back target branch, merge commit, tag, GitHub Release, npm package version, and workflow evidence.
7. Run post-merge closeout reconciliation for WI-1515/#1515/#1505, refresh status/shadow/carrier evidence, and close #1515/#1505 only after closeout checks pass.

## Ownership Constraints

- Main thread owns PR body, issue body, `.loom/status/current.md`, `.loom/progress/WI-1515.md`, `.loom/reviews/WI-1515.json`, shadow, and closeout carrier writes.
- Subagents may provide read-only release, metadata, workflow, and risk review summaries; their outputs must be integrated by the main thread before they become evidence.
- No actor may create tags, GitHub Releases, npm publications, publish-capable workflow dispatches, or merge the release PR before explicit user approval.
- #1515 must not add new gate behavior, closeout gate behavior, classifier behavior, or wrapper/runtime implementation.

## Validation

- Targeted local checks: `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `npm pack --dry-run --json --ignore-scripts`; `node bin/loom.mjs version --json`; `python3 tools/loom.py skills release-check --json`; `python3 tools/skills_surface.py check`; `python3 tools/check_cli_contract.py`; suite validate/evidence/carrier validate; fact-chain; work-item audit; `git diff --check`.
- PR metadata checks: render, preflight, create/update, readback, and gate consumption against current branch/head.
- Hosted checks: consume the release PR checks after PR creation.
- Post-merge checks: release/tag/npm/workflow readback, closeout run/check, status/shadow refresh, and #1515/#1505 issue closeout readback.

## Rollback Boundary

- Before merge: revert the release PR branch if release evidence or metadata is wrong.
- After merge but before publication completes: stop closeout and classify the workflow or host failure before retrying.
- After publication: do not rewrite release history in #1515; open a follow-up issue for corrective release evidence if needed.
