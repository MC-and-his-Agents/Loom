# WI-1296 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1296 is a bounded release convergence Work Item that publishes already-merged Round 9 behavior through existing version, npm, and GitHub release surfaces without changing runtime behavior or release workflow semantics. consumer boundary: suite validate, review, merge-ready, PR gate, hosted release-judgment, controlled merge, post-merge release closeout, parent #1228 closeout, and Round 9 milestone closeout may consume this minimal spec, plan, evidence map, task carrier, WI carriers, release workflow evidence, and host readbacks. recheck condition: require a full suite if #1296 expands into release workflow behavior changes, npm package payload changes beyond version surfaces, new runtime behavior, security/privacy decisions, schema/parser/failure vocabulary changes, or product release policy changes.

## Objective

Publish Loom CLI v0.14.1 for Round 9 idle closeout sync support and bind final release evidence into repo and GitHub closeout truth.

## Acceptance Scenarios

### S1: release target is unoccupied before merge

Given #1296 selects v0.14.1, remote git tags, GitHub Release, and npm package readback prove v0.14.1 is not already occupied before the PR is merged.

### S2: version surfaces are synchronized

Given release PR validation runs, `VERSION`, `package.json`, and every generated `skills/loom-*/loom-package.json` `repo_version` agree on v0.14.1 / 0.14.1.

### S3: release/package checks pass before merge

Given the PR is ready for merge, release surface, version surface, npm package, CLI contract, skills surface, suite evidence, PR metadata, authored review, hosted checks, and release-judgment all pass on the current PR head.

### S4: post-merge release evidence is authoritative

Given the release PR is merged to main, the `loom-cli-release` push run is bound to the merge commit and readback proves the v0.14.1 tag, GitHub Release, npm package, and installed/global CLI smoke.

### S5: terminal closeout consumes release evidence

Given release evidence is verified, WI-1296 progress/review/status/shadow carriers record terminal closeout and GitHub issue #1296 is CLOSED/COMPLETED before parent #1228 and the Round 9 milestone close.

## Non-Goals

- No release workflow behavior, package payload policy, installer legacy release line, runtime semantics, schema, parser, failure vocabulary, host mutation logic, Round 10/11, Deferred roadmap, parent #1228 closeout before #1296 completion, or unrelated refactors.
