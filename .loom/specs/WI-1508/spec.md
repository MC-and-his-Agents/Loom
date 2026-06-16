# WI-1508 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1508 is a bounded CLI/runtime implementation of the already frozen `loom-gate-freeze/v1` contract and does not change hosted workflow admission, PR template semantics, GitHub host writes, release mechanics, security permissions, data persistence outside repo-local runtime artifacts, or external visible actions. consumer boundary: CLI contract checks, generated runtime drift checks, suite validate, review, PR gate, merge-ready, and #1509-#1515 implementation planning may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence. recheck condition: require a full suite if #1508 expands into hosted workflow changes, PR template hash pinning, host truth writes, release mechanics, new security/privacy behavior, migration behavior, or external visible actions.

## Objective

Provide executable local command entrypoints for the gate input freeze snapshot so later milestone/12 hosted admission work can consume a stable `loom-gate-freeze/v1` payload.

## Acceptance Scenarios

### S1: Check is read-only

Given `loom gate freeze check --target . --json` runs, it emits `loom-gate-freeze/v1`, reports pass/block readiness, includes machine-readable blocking inputs, and does not write repo, runtime, or host truth.

### S2: Write is repo-local runtime only

Given `loom gate freeze write --target . --json` runs, it writes only `.loom/runtime/gate-freeze/<item>.json` or a caller-provided path under `.loom/runtime/gate-freeze/` and reports the artifact locator and hash.

### S3: Missing inputs fail closed

Given fact-chain, review/head, PR metadata, shadow parity, suite validation, release judgment, or command surface inputs are missing or stale, the snapshot result is `block` with source locator, consumer impact, messages, refresh suggestions, and next action.

### S4: Existing gate semantics are reused

Given existing PR metadata, shadow parity, suite validation, and review/head helpers already classify inputs, the freeze command consumes their JSON outputs or helper payloads without weakening review, PR gate, controlled merge, release/no-release, or closeout semantics.

### S5: Command matrix and generated runtime copies are aligned

Given `loom help --json`, CLI contract checks, and generated-tree drift checks run, both `gate freeze check` and `gate freeze write` are declared implemented and all shared runtime copies expose the same entrypoint.

## Non-Goals

- No PR body hash pin semantics.
- No hosted workflow admission change.
- No GitHub issue, PR, check, branch, or Project writes.
- No release/no-release closeout implementation.
- No weakening of review, PR gate, controlled merge, release/no-release, or closeout semantics.
