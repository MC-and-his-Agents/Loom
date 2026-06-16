# WI-1507 Spec

## Suite Path

- Suite path: minimal
- Full suite artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1507 is a bounded docs/governance contract freeze that defines the `loom-gate-freeze/v1` snapshot shape and examples without changing runtime behavior, CLI routing, hosted workflows, PR template behavior, generated skills payload, release mechanics, or external host settings. consumer boundary: suite validate, review, merge-ready, PR gate, hosted checks, and #1508 implementation planning may consume this minimal spec, plan, evidence map, task carrier, WI carriers, focused validation output, and PR evidence. recheck condition: require a full suite if #1507 expands into CLI implementation, workflow changes, PR template changes, generated skill payload changes, runtime parser/schema changes, release mechanics, security/privacy behavior, or external visible actions.

## Objective

Freeze the gate input snapshot contract so later milestone/12 implementation issues can consume a stable field boundary.

## Acceptance Scenarios

### S1: Snapshot fields are frozen

Given #1508 implements a CLI entry, the contract defines Work Item, branch, PR, head SHA, base SHA, PR body hash, metadata fingerprint, carrier refresh, review/head binding, shadow source hash, suite status, and release/no-release requiredness fields.

### S2: Readiness output is machine-readable

Given hosted admission consumes a snapshot, result, blocking inputs, advisory inputs, refresh suggestions, failure classifier, and next action are defined with stable field names.

### S3: Suite evidence and task carrier validation are included

Given `suite evidence validate` or `suite carrier validate` returns row-level gaps or unknown vocabulary, the snapshot records source locator, failure kind, consumer impact, next action, and contract/vocabulary drift instead of collapsing to manual investigation.

### S4: Release evidence boundary is explicit

Given a release-required change is still pre-merge, the snapshot distinguishes pre-merge release-prep evidence from post-merge release evidence and does not mark future tags, GitHub Releases, npm publish, or global CLI smoke as present.

### S5: Command suggestions are executable or explicitly unsupported

Given the snapshot suggests a repair or refresh command, the contract requires the command to exist in the current CLI command matrix or return `unsupported_command_surface` with an executable alternative path.

## Non-Goals

- No CLI implementation.
- No hosted workflow change.
- No PR template behavior change.
- No runtime gate behavior change.
- No release/no-release closeout implementation.
- No weakening of review, PR gate, controlled merge, release/no-release, or closeout semantics.
