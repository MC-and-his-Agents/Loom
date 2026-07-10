# WI-1237 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1237 is a bounded docs/help/release-surface Work Item that consumes already-stabilized #1235/#1236 behavior and updates user-facing command guidance plus release validation coverage without changing runtime behavior, host mutation semantics, shared schema, parser, failure vocabulary, workflow behavior, or package payload semantics. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, release/no-release closeout, and parent Round 9 closeout may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence. recheck condition: require a full suite if #1237 expands into runtime behavior changes, release workflow/publish behavior, package payload changes, host mutation behavior, shared schema/parser/failure vocabulary changes, security/privacy behavior, or new product/API contracts.

## Objective

Document and validate idle closeout sync guidance after #1235/#1236 stabilized the repair and fixture behavior.

## Acceptance Scenarios

### S1: README gives a recovery path

Given a user finds a HotCP-style stale active carrier after host completion, README explains the three layers and shows the readback path to `idle` / `no_active_item`.

### S2: harness docs distinguish lifecycle layers

Given maintainers inspect methodology docs, workspace retire, host closeout sync, and carrier closeout-sync are described as separate ownership layers with explicit mutation boundaries.

### S3: CLI help names the layers

Given a user runs `python3 tools/loom.py help --json`, summaries for `workspace retire`, `closeout` / `gate closeout`, `repair plan/apply`, `reconcile`, and `carrier closeout-sync` expose local-only, host sync, and carrier sync boundaries.

### S4: release readiness checks cover the story

Given release/no-release closeout consumes release-surface validation, `tools/check_release_surface.py --surface release-doc-contract` fails closed unless README and the release surface mention the command names and HotCP-style stale carrier fixture story.

## Non-Goals

- No runtime semantics, schema, parser, failure vocabulary, host mutation, workflow, package payload, VERSION, tag, GitHub Release, or npm publish changes.
- No #1296 release/no-release closeout implementation.
- No parent #1228 closeout, Round 10, Round 11, Deferred roadmap, or unrelated refactors.
