# WI-1236 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1236 is a bounded regression-fixture Work Item that consumes already-stabilized #1235 behavior and adds focused contract coverage without changing public runtime behavior, host mutation semantics, shared schema, parser, or failure vocabulary. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, and closeout may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence. recheck condition: require a full suite if #1236 expands into runtime behavior changes, docs/help finalization, release/no-release closeout, host mutation, shared schema/parser/failure vocabulary changes, security/privacy behavior, or new product/API contracts.

## Objective

Add regression fixtures matching the HotCP stale active carrier failure mode.

## Acceptance Scenarios

### S1: host-complete active carrier remains active before carrier closeout sync

Given a repo-local Work Item carrier whose GitHub issue is closed/completed and whose PR is merged while `.loom/progress/<item>.md` still has a non-terminal checkpoint, the fact-chain still points at that completed Work Item before carrier closeout sync.

### S2: workspace retire does not repair versioned carriers

Given the same stale active carrier, `loom workspace retire` reports local-only cleanup and does not mutate `.loom/progress/**`, `.loom/status/current.md`, or `.loom/bootstrap/init-result.json`.

### S3: carrier closeout sync is the repair path

Given the same stale active carrier after local workspace retire, `loom repair plan/apply --issue <n>` still exposes and applies `carrier_closeout_sync`, writes terminal metadata, switches status/init-result to idle `no_active_item`, and produces a consumable idle fact-chain.

### S4: retained historical item naming is covered

Given a retained historical item name such as `GH-21-LOOM-UPGRADE-BASELINE`, the repair plan/apply fixture still binds by explicit issue ownership and terminalizes the retained carrier without relying on canonical `WI-<issue>` naming.

## Non-Goals

- No runtime behavior changes beyond the fixture assertions already supported by #1235.
- No docs/help/release surface updates; #1237 owns those.
- No release/tag/npm/GitHub Release actions; #1296 owns release/no-release closeout.
- No Round 10, Round 11, Deferred roadmap, shared schema/parser/failure vocabulary, workflow, or unrelated refactor scope.
