# WI-1544 Spec

## Suite Path

- Suite path: not_applicable

- Formal-suite not_applicable: rationale: WI-1544 is a bounded docs/skills governance protocol slice that defines lane orchestration, ownership, stale result, conflict handling, and shared carrier serial-write rules. A formal implementation suite would restate the same protocol without adding separate runtime behavior. consumer boundary: this decision only skips formal suite artifacts; fact-chain/status carriers, current-head review, PR metadata/readback, hosted checks, PR gate, no_release judgment, controlled merge, and post-merge closeout remain required. recheck condition: require a minimal or full suite if scope expands into runtime commands, scheduler behavior, hosted workflow behavior, gate/classifier/closeout semantics, release mechanics, security/privacy behavior, migration behavior, or external visible actions. scope proof: `git diff origin/main...HEAD` must stay limited to WI-1544 carriers, `docs/methodology/harness/lane-orchestration.md`, harness README linkage, source skill references, and generated skills runtime/reference copies. review requirement: current-head review must consume the final docs/skills diff, generated surface evidence, PR metadata/readback, and proof that no runtime, hosted gate, closeout profile, classifier, release, or implementation behavior changed.

## Objective

Define the Loom lane orchestration protocol so high-throughput milestone work can use parallel read-only and owned-write lanes without parallel writes to shared truth carriers or stale subagent results being promoted as completed truth.

## Acceptance Scenarios

### S1: Lane descriptor is explicit

Given a future milestone uses subagents or lanes, the protocol requires task goal, locators, read scope, write ownership, forbidden targets, validation expectation, output format, conflict policy, and stale result policy before lane output can be integrated.

### S2: Shared truth carriers stay serial

Given multiple lanes return outputs, only the main execution line may write PR body, issue body, `.loom/status/current.md`, `.loom/progress/*`, `.loom/reviews/*`, `.loom/shadow/*`, or recovery authored fields after fresh readback.

### S3: Stale or conflicting lane output fails closed

Given a lane is behind target branch, head SHA changes, PR body readback changes, classifier/schema names drift, shared carrier hashes change, or ownership overlaps occur, the protocol blocks direct integration and sends the result back to main-thread root-cause handling.

### S4: Skills consume the protocol as execution guidance

Given `loom-build`, `loom-resume`, `loom-handoff`, and `loom-merge-ready` are used, their skill references point to the lane orchestration protocol without treating lane output as authored truth.

## Non-Goals

- No generic scheduler or background queue implementation.
- No GitHub dependency, PR slicing, review, merge-ready, PR gate, hosted gate, or closeout gate replacement.
- No runtime command implementation.
- No failure classifier vocabulary changes.
- No closeout terminal profile semantic changes.
- No release, tag, npm, or external host setting changes.
